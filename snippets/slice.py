




class MakeSlice:
    def __getitem__(self, sl):
        return sl
    
make_slice = MakeSlice()
lst = list(range(36))

sl = make_slice[34:36]

print(len(lst))

print(sl)
print(sl.indices(len(lst)))
print(lst[sl])


sl = make_slice[34:]
print(sl)
print(sl.indices(len(lst)))
print(lst[sl])
