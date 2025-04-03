import math


class TimeDelta:

    def __init__(self, hour: int, minute: int):
        self.hour = hour
        self.minute = minute

    @property
    def hour(self) -> int:
        return self._hour

    def f(self):
        pass

    @hour.setter
    def hour(self, h: int) -> None:
        if(h >= 0 and h < 24):
            self._hour = h
        else:
            raise ValueError("Hour difference needs to be greater equal to 0 or less than 24 hours")

    @property
    def minute(self) -> int:
        return self._minute

    @minute.setter
    def minute(self, m: int) -> None:
        if(m % 15 == 0):
            if(m <= 45):
                self._minute = m
            else:
                self._minute = (math.floor(m/15) % 4) * 15
                self.hour += math.floor(m/60)
        else:
            raise ValueError("Minute diff must be a multiple of 0 or a multiple of 15")


class Time:

    def __init__(self, hour: int, minute: int, am=None):
        if hour > 12 and am != None:
            print('Error: 24 hour time you must leave am set to None')
        self.am = am
        self.hour = hour
        self.minute = minute

    # hour stuff
    @property
    def hour(self) -> int:
        return self._hour

    @hour.setter
    def hour(self, h: int) -> None:
        if h >= 1 and h <= 12:
            self._hour = h
        elif h > 12:
            # see how many flips of am or pm and apply net
            if math.floor(h/12) % 2 == 0:
                self.am = True
            else:
                self.am = False

            # apply correct hour between 1 and 12
            if h % 12 == 0:
                self._hour = 12
            else:
                self._hour = h % 12
        elif h < 1:
            if math.floor(h/12) % 2 == -1:
                self.am = False
            else:
                self.am = True
            self._hour = 12 + h % 12

    # minute stuff
    @property
    def minute(self) -> int:
        return self._minute

    @minute.setter
    def minute(self, m: int) -> None:
        # has to be a multiple of 15 as this is all we can set in eleads for appointment (such as 0, 15, 30, or 45)
        if m % 15 == 0:
            # self._minute = m
            if m > 45 or m < 0:
                h = math.floor(m / 60)
                self.hour += h
                m -= h*60
                self.minute = m # recursive call
            else:
                self._minute = m
        else:
            raise ValueError("Minute diff must be 0, 15, 30, or 45")

    @property
    def am(self) -> bool:
        return self._am

    @am.setter
    def am(self, b: bool) -> None:
        self._am = b

    # dunder function string representation
    def __repr__(self) -> str:
        return f'{self.hour}:{self.minute if self.minute > 0 else "00"} {"AM" if self.am else "PM"}'

    # converts to minutes past midnight
    def totalMinutes(self) -> int:
        hour = self.hour if self.hour != 12 else 0
        if(self.am == False):
            hour += 12

        totalMinutes = self.minute + hour * 60
        if totalMinutes >= 1440:
            print("Error: total minutes too great")
        else:
            return self.minute + hour * 60

    def flipAM(self):
        if self.am == True:
            self.am = False
        else:
            self.am = True

    # dunder function <
    def __lt__(self, other): # I want to put 'other: Time' but it isn't letting me for some reason
        # check I have to do because it won't let me do what is comment up above
        if not isinstance(self, Time) and not isinstance(other, Time):
            print("Error: comparison must be between to Time type objects")
            return None
        if self.totalMinutes() < other.totalMinutes():
            return True
        else:
            return False

    # dunder function <=
    def __le__(self, other): # ref comments above on __lt__ function
        if not isinstance(self, Time) and not isinstance(other, Time): # ref comments above on __lt__ function
            print("Error: comparison must be between to Time type objects")
            return None
        if self.totalMinutes() <= other.totalMinutes():
            return True
        else:
            return False

    # dunder function >
    def __gt__(self, other):
        if not isinstance(self, Time) and not isinstance(other, Time):
            print("Error: comparison must be between to Time type objects")
            return None
        if self.totalMinutes() > other.totalMinutes():
            return True
        else:
            return False

    # dunder function >=
    def __ge__(self, other):
        if not isinstance(self, Time) and not isinstance(other, Time):
            print("Error: comparison must be between to Time type objects")
            return None
        if self.totalMinutes() >= other.totalMinutes():
            return True
        else:
            return False

    # dunder function ==
    def __eq__(self, other):
        if not isinstance(self, Time) and not isinstance(other, Time):
            print("Error: comparison must be between to Time type objects")
            return None
        if self.totalMinutes() == other.totalMinutes():
            return True
        else:
            return False

    # dunder function !=
    def __ne__(self, other):
        if not isinstance(self, Time) and not isinstance(other, Time):
            print("Error: comparison must be between to Time type objects")
            return None
        if self.totalMinutes() != other.totalMinutes():
            return True
        else:
            return False

    # dunder method +=
    def __iadd__(self, td: TimeDelta):
        hour_start = self.hour
        self.hour += td.hour
        self.minute += td.minute
        # if we flipped to 12 flip the am/pm
        if hour_start < 12 and self.hour == 12:
            self.flipAM()
        return self

    # dunder method -=
    def __isub__(self, td: TimeDelta):
        hour_start = self.hour
        self.hour -= td.hour
        self.minute -= td.minute
        #if hour_start < self.hour and self.hour != 12:
        #    self.flipAM()
        return self

    # dunder method for add
    def __add__(self, td: TimeDelta):
        # TODO: need to fix this later
        t = Time(self.hour, self.minute, self.am)
        # if self.hour == 12 and self.am == True: # to fix a bug  with large time delta and st at 12am
        #     t += TimeDelta(td.hour - 12, td.minute)
        # else:
        t += td
        return t

    # dunder method for subtract
    def __sub__(self, td: TimeDelta):
        t = Time(self.hour, self.minute, self.am)
        t -= td
        return t

