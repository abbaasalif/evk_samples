#include <fstream>
#include <thread>
#include <regex>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <atomic>
#include <iostream>
#include <boost/program_options.hpp>
#include <metavision/sdk/base/utils/log.h>
#include <metavision/sdk/driver/camera_exception.h>
#include <metavision/sdk/driver/camera.h>

namespace po = boost::program_options;

// Thread-safe queue for event storage
class ThreadSafeQueue {
public:
    void push(const Metavision::EventCD &event) {
        std::lock_guard<std::mutex> lock(mutex_);
        queue_.push(event);
        cond_.notify_one();
    }

    bool pop(Metavision::EventCD &event) {
        std::unique_lock<std::mutex> lock(mutex_);
        cond_.wait(lock, [this] { return !queue_.empty() || stop_; });
        if (stop_ && queue_.empty()) return false;
        event = queue_.front();
        queue_.pop();
        return true;
    }

    void stop() {
        std::lock_guard<std::mutex> lock(mutex_);
        stop_ = true;
        cond_.notify_all();
    }

private:
    std::mutex mutex_;
    std::condition_variable cond_;
    std::queue<Metavision::EventCD> queue_;
    bool stop_ = false;
};

// CSV writer that uses ThreadSafeQueue
class CSVWriter {
public:
    CSVWriter(const std::string &filename) : ofs_(filename, std::ofstream::out) {
        if (!ofs_.is_open()) {
            throw std::runtime_error("Unable to write to file");
        }
        writer_thread_ = std::thread(&CSVWriter::writeLoop, this);
    }

    ~CSVWriter() {
        queue_.stop();
        writer_thread_.join();
    }

    void write(const Metavision::EventCD &event) {
        queue_.push(event);
    }

private:
    void writeLoop() {
        Metavision::EventCD event;
        while (queue_.pop(event)) {
            ofs_ << event.x << "," << event.y << "," << event.p << "," << event.t << "\n";
        }
    }

    std::ofstream ofs_;
    ThreadSafeQueue queue_;
    std::thread writer_thread_;
};

int main(int argc, char *argv[]) {
    std::string in_file_path;
    std::string out_file_path;

    po::options_description options_desc("Options");
    options_desc.add_options()
        ("help,h", "Produce help message.")
        ("input-file,i", po::value<std::string>(&in_file_path)->required(), "Path to the input file.")
        ("output-file,o", po::value<std::string>(&out_file_path)->default_value(""), "Path to the output file.");

    po::variables_map vm;
    try {
        po::store(po::parse_command_line(argc, argv, options_desc), vm);
        po::notify(vm);
        if (vm.count("help")) {
            std::cout << options_desc << std::endl;
            return 0;
        }
    } catch (po::error &e) {
        std::cerr << "Error: " << e.what() << std::endl;
        std::cerr << options_desc << std::endl;
        return 1;
    }

    if (out_file_path.empty()) {
        const std::string output_base = std::regex_replace(in_file_path, std::regex("\\.[^.]*$"), "");
        out_file_path = output_base + ".csv";
    }

    Metavision::Camera cam;
    try {
        cam = Metavision::Camera::from_file(in_file_path, Metavision::FileConfigHints().real_time_playback(false));
    } catch (Metavision::CameraException &e) {
        std::cerr << "CameraException: " << e.what() << std::endl;
        return 1;
    }

    CSVWriter writer(out_file_path);

    cam.cd().add_callback([&writer](const Metavision::EventCD *ev_begin, const Metavision::EventCD *ev_end) {
        for (const Metavision::EventCD *ev = ev_begin; ev != ev_end; ++ev) {
            writer.write(*ev);
        }
    });

    cam.start();
    while (cam.is_running()) {
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    };

    return 0;
}
