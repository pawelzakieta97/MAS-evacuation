from heapq import heappop, heappush, heappushpop

g = []  # heap queue
iteration = 0

open_set = set()
closed_set = set()

# open_set.add(s[1])
#
# start = time.time()

a = 'asdasdasd'

heappush(g, (1, a))
heappush(g, (4, a))
heappush(g, (3, '3'))
heappush(g, (2, '2'))
print(g)
print(heappop(g))
print(g)
# while s[1].h() > 0:
#     for i in s[1].generate_children():
#         if i not in closed_set and i not in open_set:
#             heappush(g, (i.f(), i))
#             open_set.add(i)
#
#     open_set.remove(s[1])
#     closed_set.add(s[1])
#
#     s = heappop(g)
#
#     iteration += 1