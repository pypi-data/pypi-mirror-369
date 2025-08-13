class StreamingStats:
    def __init__(self, number=None):
        if number is None:
            self.n = 0
            self.mean = 0.0
            self.m2 = 0.0
            self.x3 = 0.0
            self.median = 0
            self.min = 0
            self.max = 0
        else:
            self.n = 1
            self.mean = round(number, 3)
            self.m2 = 0.0
            self.x3 = 0.0
            self.median = round(number, 3)
            self.min = round(number, 3)
            self.max = round(number, 3)

    def update(self, x):
        self.n += 1
        
        # Variance
        delta = round(x - self.mean, 3)
        self.mean += round(delta / self.n, 3)
        delta2 = round(x - self.mean, 3)
        self.m2 += round(delta * delta2, 3)
        
        # skewness
        self.x3 += round(x**3, 3)

        # Median
        self.median += round((x - self.median) / self.n, 3)

        # Min
        if self.n == 1:
            self.min = round(x, 3)
        else:
            self.min = round(min(self.min, x), 3)
        # Max
        self.max = round(max(self.max, x), 3)
    
    def merge(self, other):
        if other == None or isinstance(other, int):
            return self
        
        combined = StreamingStats()
        combined.n = self.n + other.n

        combined.x3 = round(self.x3 + other.x3, 3)

        delta = other.mean - self.mean
        combined.mean = round((self.n * self.mean + other.n * other.mean) / combined.n, 3)

        combined.m2 = self.m2 + other.m2 + delta**2 * self.n * other.n / combined.n

        combined.min = min(self.min, other.min) if self.min is not None and other.min is not None else self.min or other.min
        combined.max = max(self.max, other.max) if self.max is not None and other.max is not None else self.max or other.max

        combined.median = round((self.median * self.n + other.median * other.n) / (self.n + other.n), 3)

        return combined
    
    def get_mean(self):
        return round(self.mean, 2)
    
    # reservoir sampling technique
    def get_median(self):
        return round(self.median, 2)
    
    def get_variance(self):
        return round(self.m2 / self.n if self.n > 1 else 0.0, 2)
    
    def get_std(self):
        return round((self.get_variance())**0.5, 2)
    
    def get_skewness(self):
        if self.m2 == 0 or self.n < 2:
            return 0.0
        return round((self.x3 - (self.mean**3)*self.n - 3*((self.get_variance() + self.mean**2) * self.n)*self.mean + 3*(self.mean**3)*self.n)/((self.n-1)*((self.m2 / self.n)**0.5)**3), 2)
    
    def get_min(self):
        return round(self.min, 2)
    
    def get_max(self):
        return round(self.max, 2)
    
    def get_total(self):
        return round(self.mean*self.n, 2)

