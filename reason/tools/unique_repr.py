from typing import List

from collections import Counter

class UniqueRepr:

    @staticmethod
    def merge_unique_sorted_lists(list1, list2):
        """
        Merge two sorted lists of unique integers into one sorted list of unique integers.
        """
        i, j = 0, 0
        merged = []

        while i < len(list1) and j < len(list2):
            if list1[i] < list2[j]:
                # Add list1[i] if it's not a duplicate of the last added element
                if not merged or merged[-1] != list1[i]:
                    merged.append(list1[i])
                i += 1
            elif list1[i] > list2[j]:
                # Add list2[j] if it's not a duplicate of the last added element
                if not merged or merged[-1] != list2[j]:
                    merged.append(list2[j])
                j += 1
            else:
                # They are equal; add one of them (avoid duplicates)
                if not merged or merged[-1] != list1[i]:
                    merged.append(list1[i])
                i += 1
                j += 1

        # Add remaining elements from list1 (if any), skipping duplicates
        while i < len(list1):
            if not merged or merged[-1] != list1[i]:
                merged.append(list1[i])
            i += 1

        # Add remaining elements from list2 (if any), skipping duplicates
        while j < len(list2):
            if not merged or merged[-1] != list2[j]:
                merged.append(list2[j])
            j += 1

        return merged

    @staticmethod
    def reduce_counter(counter):
        res = UniqueRepr()

        for key in counter:
            if counter[key] % 2 != 0:
                res.addends.append(key)

        return res

    def __init__(self, value : int | List[int] = None):
        self.addends = []

        match value:
            case int():
                self.addends = ((value,),)
            case [*elements]:
                elements.sort()
                self.addends = [tuple(elements)]

    def __add__(self, other):
        counter = Counter(self.addends)
        counter.update(other.addends)

        return self.reduce_counter(counter)

    def __mul__(self, other):
        candidates = []
        for a in self.addends:
            for b in other.addends:
                if b == (1,):
                    candidates.append(a)
                elif a == (1,):
                    candidates.append(b)
                else:
                    candidates.append(tuple(self.merge_unique_sorted_lists(a, b)))

        counter = Counter(candidates)

        return self.reduce_counter(counter)

    def get_sorted(self):
        return sorted(self.addends)






