import speedtest
import threading

class SpeedtestManager:
    @staticmethod
    def run_speedtest(progress_callback=None,result_callback=None, error_callback=None):
        def _test():
            try:
                if progress_callback:progress_callback("Finding best server...")
                st = speedtest.Speedtest(secure=True, timeout=5)
                st.get_best_server()

                if progress_callback: progress_callback("Testing download speed...")
                download_speed = st.download()/1_000_000

                if progress_callback: progress_callback("Testing upload speed...")
                upload_speed = st.upload() / 1_000_000

                ping = st.results.ping
                if result_callback: result_callback(ping, download_speed, upload_speed)

            except Exception as e:
                if error_callback: error_callback(str(e))
            
        thread = threading.Thread(target=_test, daemon=True)
        thread.start()