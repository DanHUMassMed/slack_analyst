import uuid

class SessionState:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SessionState, cls).__new__(cls, *args, **kwargs)
            cls._instance.init()
        return cls._instance
    
    def init(self):
        self.data = {}
        
    def session_data(self, session_id):
        data = self.data.get(session_id, None)
        if not data:
            self.data[session_id] = {}
        
        return self.data[session_id]