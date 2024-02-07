class BaseCoroutineCondtion():
    def __init__(self, context) -> None:
        self.context = context
    
    def check(self):
        return True
    
class CoroutineWaitForSeconds(BaseCoroutineCondtion):
    def __init__(self, context, time:float) -> None:
        super().__init__(context)
        self.target_time = time + self.context.get_time()
        
    def check(self):
        if (self.context.get_time() >= self.target_time):
            return True
        return False
        
class CoroutineEnd(BaseCoroutineCondtion):
    def __init__(self, context) -> None:
        super().__init__(context)
    