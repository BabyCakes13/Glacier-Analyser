"""
Class which holds multiprocessing handling.
"""
import signal
import subprocess

from colors import *

import definitions


class Multiprocess:
    """
    Class which handles multiprocessing.
    """

    def __init__(self, max_processes=definitions.MAX_PROCESSES, handler=None):
        """
        Initializes the maximum number of processes, as well as the process queue and the handler function which will
        run the after a process has finished from the queue.
        :param max_processes: Number of maximum processes to run simultaneously.
        :param handler: The method which runs each time a process has finished.
        """
        self.max_processes = max_processes
        self.process_queue = []
        self.handler = handler

    def start_processing(self, task, task_name) -> None:
        """
        Waits for a spot to free in the queue of processes, and when one finished, the pending one is appended to the
        list and started.
        :param task: Task to process.
        :param task_name: Name of the task to process, for visual debugging and interpretation.
        :return: None
        """
        self.poll_process_done()
        print(blue("Processes in queue before add: "), blue(len(self.process_queue)))

        sp = subprocess.Popen(task)
        self.process_queue.append((task_name, sp))

        print(blue("Processes in queue after add: "), blue(len(self.process_queue)))

    def check_process_full(self) -> None:
        """
        Checks if the process queue is full; if it is, it pops the last one out and starts processing it.
        :return: None
        """
        if len(self.process_queue) >= self.max_processes:
            task_name, sp = self.process_queue.pop()
            sp.wait()

    def check_process_done(self):
        """
        Checks the process queue list for terminated processes; if found, it removes it and calls the handler function
        to interpret the results of the return code of the subprocess.
        :return:
        """
        for task_name, sp in self.process_queue:
            if sp.poll() is not None:
                self.process_queue.remove((task_name, sp))
                print(blue("Query done: "), blue(task_name))
                if self.handler is not None:
                    self.handler(task_name, sp.returncode)

    def poll_process_done(self) -> None:
        """
        Keeps asking IS IT DONE YET?
        :return: None
        """
        while len(self.process_queue) >= self.max_processes:
            self.check_process_done()

    def wait_all_process_done(self) -> None:
        """
        Waits till all the processes from the process queue are done.
        :return: None
        """
        while len(self.process_queue) > 0:
            self.check_process_done()

    def kill_all_processes(self) -> None:
        """
        If interrupt key is pressed, it signals each process to terminate.
        :return: None
        """
        for task_name, sp in self.process_queue:
            sp.send_signal(signal.SIGINT)