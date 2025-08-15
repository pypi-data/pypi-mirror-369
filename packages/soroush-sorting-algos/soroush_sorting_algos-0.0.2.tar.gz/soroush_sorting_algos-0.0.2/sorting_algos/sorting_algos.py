import copy
import time
import random


def swap_arr_items(arr: list, i: int, j: int):
    temp = arr[i]
    arr[i] = arr[j]
    arr[j] = temp


def get_smallest_list_item_index(arr: list, start: int, end: int) -> int:
    smallest_index = start

    for index in range(start, end):
        if arr[index] < arr[smallest_index]:
            smallest_index = index

    return smallest_index


# SORT ALGO

def sort(arr_list: list) -> list:
    for arr_index in range(len(arr_list)):
        for arr_inner_index in range(arr_index + 1, len(arr_list)):
            if arr_list[arr_index] > arr_list[arr_inner_index]:
                swap_arr_items(arr_list, arr_index, arr_inner_index)

    return arr_list


def selection_sort(arr_list: list) -> list:
    for index in range(len(arr_list)):
        smallest_index = get_smallest_list_item_index(arr_list, index, len(arr_list))
        swap_arr_items(arr_list, index, smallest_index)

    return arr_list


def bubble(arr_list: list, size: int):
    last_index = size - 1
    for index in range(size):
        if last_index == index:
            return arr_list
        a_index = last_index - index

        b_index = a_index - 1
        a = arr_list[a_index]
        b = arr_list[b_index]

        if a < b:
            swap_arr_items(arr_list, a_index, b_index)


def bubble_sort(arr_list: list) -> list:
    size = len(arr_list)

    if size < 2:
        return arr_list

    for _ in range(size):
        bubble(arr_list, size)
    return arr_list



def reverse_bubble(arr_list: list) :
    for index in range(len(arr_list) - 1):
        if index == len(arr_list) - 1:
            return arr_list

        a_index = index
        b_index = a_index + 1

        a = arr_list[a_index]
        b = arr_list[b_index]

        if a > b:
            swap_arr_items(arr_list, a_index, b_index)



def reverse_bubble_sort(arr_list:list) -> list:
    size = len(arr_list)
    if size < 2:
        return arr_list

    for _ in range(size):
        reverse_bubble(arr_list)

    return arr_list

def insert_nth(arr_list: list, n: int):
    nth_value = arr_list[n]
    left_item_index = n - 1

    while left_item_index >= 0 and arr_list[left_item_index] > nth_value:
        arr_list[left_item_index + 1] = arr_list[left_item_index]
        left_item_index = left_item_index - 1

    arr_list[left_item_index + 1] = nth_value


def insertion_sort(arr_list: list) -> list:
    for index in range(1, len(arr_list)):
        insert_nth(arr_list, index)

    return arr_list


def combine(sorted_arr_list: list, start_index: int, middle_index: int, end_index: int):
    temp_arr_list = copy.copy(sorted_arr_list)

    first_half_head = start_index
    second_half_head = middle_index + 1

    result_arr_head = first_half_head

    while first_half_head <= middle_index and second_half_head <= end_index:
        if sorted_arr_list[first_half_head] <= temp_arr_list[second_half_head]:
            sorted_arr_list[result_arr_head] = temp_arr_list[first_half_head]
            first_half_head += 1
        else:
            sorted_arr_list[result_arr_head] = temp_arr_list[second_half_head]
            second_half_head += 1

        result_arr_head += 1

    while first_half_head <= middle_index:
        sorted_arr_list[result_arr_head] = temp_arr_list[first_half_head]
        first_half_head += 1
        result_arr_head += 1

    while second_half_head <= end_index:
        sorted_arr_list[result_arr_head] = temp_arr_list[second_half_head]
        second_half_head += 1
        result_arr_head += 1


def merge_sort(arr_list: list, start_index: int, end_index: int) -> list:
    if start_index >= end_index:
        return arr_list

    middle_index = (start_index + end_index) // 2

    merge_sort(arr_list, start_index, middle_index)
    merge_sort(arr_list, middle_index + 1, end_index)

    combine(arr_list, start_index, middle_index, end_index)

    return arr_list


if __name__ == "__main__":
    arr = [random.randint(-100, 100) for _ in range(5)]
    # arr = [-1, 0, -10]
    start = time.perf_counter()
    # sort(arr)
    # selection_sort(arr)
    # bubble_sort(arr)
    reverse_bubble_sort(arr)
    # insertion_sort(arr)
    # merge_sort(arr, 0, len(arr) - 1)
    end = time.perf_counter()

    print(arr)
    print(f"Duration: {(end - start):.6f} seconds")
