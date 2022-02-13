"""Api tester module made by KompocikDot"""
from api_tester import Solver
from kthread import KThread

def main():
    """Runs concurrent threads"""
    threads = []
    for item_id in range(1, 3):
        threads.append(KThread(target=Solver(item_id).run))
        threads[-1].start()

    for thread_i in threads:
        thread_i.join()


if __name__ == "__main__":
    main()
