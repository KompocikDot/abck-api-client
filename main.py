"""Api tester module made by KompocikDot"""
from kthread import KThread
from api_tester import Solver

def main():
    """Runs concurrent threads"""
    threads = []
    for item_id in range(1, 10):
        threads.append(KThread(target=Solver(item_id).run))
        threads[-1].start()

    for thread_i in threads:
        thread_i.join()


if __name__ == "__main__":
    main()
