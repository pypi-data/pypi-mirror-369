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
                if isinstance(new_data[0],list) or isinstance(new_data[0],tuple):
                    new_data = list(lotl(new_data).chain())
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
            for i in range(self.nth):
                if isinstance(new_data[0],list) or isinstance(new_data[0],tuple):
                    new_data = list(lotl(new_data).chain())
                if any([True if isinstance(i,list) or isinstance(i,tuple) else False for i in new_data]):
                    add = []
                    for i in new_data:
                        if isinstance(i,list) or isinstance(i,tuple):
                            add += i
                        else:
                            add.append(i)
                    new_data = list(add[:])
        return new_data

    def mean(self):
        return sum(self.data) / len(self.data)

    def outlier(self):
        slope = lotl(self.data).slope()
        hits = [self.data[i+1] for i in range(len(self.data)-1) if self.data[i] + slope <= self.data[i+1]]
        return hits

    def slope(self):
        x = [i for i in range(1,len(self.data)+1)]
        hits = lotl([(self.data[i+1]- self.data[i]) / (x[i+1] - x[i])  for i in range(len(self.data)-1)]).mean()
        return hits
