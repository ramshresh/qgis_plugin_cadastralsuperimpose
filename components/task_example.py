import random
from time import sleep

from qgis.core import (
    QgsApplication, QgsTask, QgsMessageLog, Qgis
    )



class RandomIntegerSumTask(QgsTask):
    """
    This shows how to subclass QgsTask
    https://docs.qgis.org/3.16/en/docs/pyqgis_developer_cookbook/tasks.html

    IMPORTANT!!!: About Usage
    #https://gis.stackexchange.com/questions/296175/issues-with-qgstask-and-task-manager
    #As @Subgenius said, a workaround would be to create the task variable with global scope.
    globals()['task1'] = RandomIntegerSumTask('Task', 20) 
    QgsApplication.taskManager().addTask(globals()['task1'])
                
    INFO:
    In this example RandomIntegerSumTask extends QgsTask and will generate 100 random 
    integers between 0 and 500 during a specified period of time. 
    If the random number is 42, the task is aborted and an exception is raised. 
    Several instances of RandomIntegerSumTask (with subtasks) are generated 
    and added to the task manager, demonstrating two types of dependencies.

    Usage:
    longtask = RandomIntegerSumTask('waste cpu long', 20)
    shorttask = RandomIntegerSumTask('waste cpu short', 10)
    minitask = RandomIntegerSumTask('waste cpu mini', 5)
    shortsubtask = RandomIntegerSumTask('waste cpu subtask short', 5)
    longsubtask = RandomIntegerSumTask('waste cpu subtask long', 10)
    shortestsubtask = RandomIntegerSumTask('waste cpu subtask shortest', 4)

    # Add a subtask (shortsubtask) to shorttask that must run after
    # minitask and longtask has finished
    shorttask.addSubTask(shortsubtask, [minitask, longtask])
    # Add a subtask (longsubtask) to longtask that must be run
    # before the parent task
    longtask.addSubTask(longsubtask, [], QgsTask.ParentDependsOnSubTask)
    # Add a subtask (shortestsubtask) to longtask
    longtask.addSubTask(shortestsubtask)

    QgsApplication.taskManager().addTask(longtask)
    QgsApplication.taskManager().addTask(shorttask)
    QgsApplication.taskManager().addTask(minitask)
    """

    def __init__(self, description, duration):
        super().__init__(description, QgsTask.CanCancel)
        self.duration = duration
        self.total = 0
        self.iterations = 0
        self.exception = None
        self.MESSAGE_CATEGORY = 'RandomIntegerSumTask'

    def run(self):
        """Here you implement your heavy lifting.
        Should periodically test for isCanceled() to gracefully
        abort.
        This method MUST return True or False.
        Raising exceptions will crash QGIS, so we handle them
        internally and raise them in self.finished
        """
        QgsMessageLog.logMessage('Started task "{}"'.format(
                                     self.description()),
                                 self.MESSAGE_CATEGORY, Qgis.Info)
        wait_time = self.duration / 100
        for i in range(100):
            sleep(wait_time)
            # use setProgress to report progress
            self.setProgress(i)
            arandominteger = random.randint(0, 500)
            self.total += arandominteger
            self.iterations += 1
            # check isCanceled() to handle cancellation
            if self.isCanceled():
                return False
            """
            # simulate exceptions to show how to abort task
            if arandominteger == 42:
                # DO NOT raise Exception('bad value!')
                # this would crash QGIS
                self.exception = Exception('bad value!')
                return False
            """
        return True

    def finished(self, result):
        """
        This function is automatically called when the task has
        completed (successfully or not).
        You implement finished() to do whatever follow-up stuff
        should happen after the task is complete.
        finished is always called from the main thread, so it's safe
        to do GUI operations and raise Python exceptions here.
        result is the return value from self.run.
        """
        if result:
            QgsMessageLog.logMessage(
                'RandomTask "{name}" completed\n' \
                'RandomTotal: {total} (with {iterations} '\
              'iterations)'.format(
                  name=self.description(),
                  total=self.total,
                  iterations=self.iterations),
              self.MESSAGE_CATEGORY, Qgis.Success)
            
        else:
            if self.exception is None:
                QgsMessageLog.logMessage(
                    'RandomTask "{name}" not successful but without '\
                    'exception (probably the task was manually '\
                    'canceled by the user)'.format(
                        name=self.description()),
                    self.MESSAGE_CATEGORY, Qgis.Warning)
            else:
                QgsMessageLog.logMessage(
                    'RandomTask "{name}" Exception: {exception}'.format(
                        name=self.description(),
                        exception=self.exception),
                    self.MESSAGE_CATEGORY, Qgis.Critical)
                raise self.exception

    def cancel(self):
        QgsMessageLog.logMessage(
            'RandomTask "{name}" was canceled'.format(
                name=self.description()),
            self.MESSAGE_CATEGORY, Qgis.Info)
        super().cancel()


from functools import partial
from qgis.core import (QgsTaskManager, 
                       QgsProcessingAlgRunnerTask, 
                       QgsProcessingContext, QgsProcessingFeedback,
                       QgsProject)

