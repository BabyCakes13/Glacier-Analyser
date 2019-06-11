from colors import *
import definitions
import signal
import subprocess

COMMANDS = ('data_processing/alignment_ORB.py', '--download')


class Multithread:
    def __init__(self, task, target_file, process_queue, max_threads=definitions.MAX_THREADS):
        self.task = task
        self.target_file = target_file
        self.max_threads = max_threads
        self.process_queue = process_queue
        self.command = self.check_task_type()

    def start_processing(self):
        self.poll_process_done()
        print(" current processes nr ", len(self.process_queue))

        sp = subprocess.Popen(self.task)
        self.process_queue.append((self.target_file, sp))
        print(" after processes nr ", len(self.process_queue))

        return self.process_queue

    def check_process_full(self):
        """Checks if the process queue is full."""
        if len(self.process_queue) >= self.max_threads:
            filename, sp = self.process_queue.pop()
            sp.wait()
            print("Query done: ", filename)

    def check_process_done(self):
        """Checks if a process from the process queue is done, removes if so."""
        for filename, sp in self.process_queue:
            if sp.poll() is not None:
                self.process_queue.remove((filename, sp))
                print("Query done: ", filename)
                self.display_results(sp, self.command)

    def poll_process_done(self):
        """Keep asking if done."""
        while len(self.process_queue) >= self.max_threads:
            self.check_process_done()

    def wait_all_process_done(self):
        """Checks if a process from the process queue is done, removes if so."""
        while len(self.process_queue) > 0:
            self.check_process_done()

    @staticmethod
    def display_results(sp, command):
        # align
        if command == COMMANDS[0]:
            if sp.returncode == 0:
                print(green("SUCCESS"))
            elif sp.returncode == 3:
                print(yellow("INTERRRUPTED"))
            elif sp.returncode == 1:
                print(red("FAILURE"))
            else:
                print(magenta("SOME OTHER ERROR"))
        elif command == COMMANDS[1]:
            print(green("downloading..."))

    def check_task_type(self):
        """
        Check the type of command inputted so the wait processes done knows what to do in each case.
        :return: The command if found, None otherwise.
        """
        for task in self.task:
            for command in COMMANDS:
                if command == task:
                    return task
        return None

    def kill_all_humans(self):
        for filename, sp in self.process_queue:
            print(red("INTRERUPTED"))
            sp.send_signal(signal.SIGINT)