class lotl:
    def __init__(self,data,nth=-1):
        self.data = data
        self.nth = nth

    def chain(self):
        hits = []
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                hits.append(self.data[i][j])
        return hits
    
    def flatten(self):
        new_data = self.data
        if self.nth == -1:
            while True:
                if any([True if isinstance(i,list) or isinstance(i,tuple) else False for i in new_data]):
                    add = []
                    for i in new_data:
                        if isinstance(i,list) or isinstance(i,tuple):
                            add += i
                        else:
                            add.append(i)
                    new_data = list(add[:])
                else:
                    break
        else:
            for _ in range(self.nth):
                if any([True if isinstance(i,list) or isinstance(i,tuple) else False for i in new_data]):
                    add = []
                    for i in new_data:
                        if isinstance(i,list) or isinstance(i,tuple):
                            add += i
                        else:
                            add.append(i)
                    new_data = list(add[:])
                else:
                    break
        return new_data

    def mean(self):
        return sum(self.data) / len(self.data)

    def nested(self):
        count = 0
        new_data = self.data
        if self.nth == -1:
            while True:
                if any([True if isinstance(i,list) or isinstance(i,tuple) else False for i in new_data]):
                    count += 1
                    add = []
                    for i in new_data:
                        if isinstance(i,list) or isinstance(i,tuple):
                            add += i
                        else:
                            add.append(i)
                    new_data = list(add[:])
                else:
                    break
        return count

    def slope(self):
        x = [i for i in range(1,len(self.data)+1)]
        hits = lotl([(self.data[i+1]- self.data[i]) / (x[i+1] - x[i])  for i in range(len(self.data)-1)]).mean()
        return hits

    def zero(self):
        if isinstance(self.data, int):
            return [0 for i in range(self.data)]
        elif isinstance(self.data,list) or isinstance(self.data,tuple):
            if len(self.data) == 2:
                return [[0 for j in range(self.data[0])] for i in range(self.data[1])]
