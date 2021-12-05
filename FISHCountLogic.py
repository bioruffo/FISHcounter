# -*- coding: utf-8 -*-
"""
Created on Thu May 31 17:36:32 2018

@author: Roberto
"""


class Keys(object):
    def __init__(self, keys):
        self.keys = [ord(key) for key in keys if key != 'n/a']
        self._do_reverse()

    def _do_reverse(self):
        self.positions = dict([(keystroke, i) for i, keystroke in enumerate(self.keys)])

    def alter(self, position, newkey):
        print(self.keys)
        print(position)
        self.keys[position] = newkey
        self._do_reverse()
    
    def get_position(self, key):
        return self.positions.get(key, None)
        
    
class Counts(object):
    def __init__(self, base_values = None):
        if not base_values:
            self.values = [0, 0, 0, 0, 0, 0]
        else:
            assert type(base_values) == list and len(base_values) == 6 and all([type(x) == int for x in base_values])
            self.values =  base_values
    
    def do_increment(self, position):
        self.values[position] += 1

    def do_decrement(self, position):
        self.values[position] -= 1
        
    def get_sum(self):
        return sum(self.values)
    
    def get_bar(self, bar):
        return self.values[bar]


class Logic(object):
    def __init__(self, goal = 200, keys = list(range(49,55)), current_counts = None): # keys 49-54 = keys from 1 to 6
        self.keys = Keys(keys)
        self.last_positions = [None for i in range(5)]
        if not current_counts:
            self.counts = Counts()
        else:
            self.counts = Counts(current_counts)
        self.set_goal(goal)
   
    
    def get_progress(self, pool = None, rettype = int):
        assert (pool == None) or (type(pool) == int and 0 <= pool < 6)
        if pool is None:
            total = self.counts.get_sum()
        else:
            total = self.counts.values[pool] # list is 0-based
        return rettype((100 * total) / self.goal)
  
    
    def set_goal(self, newgoal):
        self.goal = newgoal
        # TODO remember that bars are only estat start, need to update
        
    def register(self, key):
        if not self.is_goal_reached():
            position = self.keys.get_position(key)
            self.last_positions = self.last_positions[1:] + [position]
            self.counts.do_increment(position)
            return True
        else:
            return False


    def sort_categories(self):
        totcount = self.counts.get_sum()
        if totcount > 0:
            return sorted(range(6), key=lambda x:self.counts.values[x], reverse=True)
        else:
            return [0 for i in range(6)]

    def undo(self):
        if self.last_positions[-1] == None:
            return False
        else:
            removed = self.last_positions[-1]
            self.last_positions = [None] + self.last_positions[:-1]
            if removed != None:
                self.counts.do_decrement(removed)
                return True
            else:
                return False
            
        
    
    def is_key(self, key):
        return key in self.keys.keys
    
    def is_goal_reached(self):
        return self.counts.get_sum() >= self.goal
        
    def reset_counts(self, base_values = None):
        self.counts = Counts(base_values)
        self.last_positions = [None for i in range(5)]
        
