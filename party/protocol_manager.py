from protocol_finder import PROTOCOLS
from util.paths import extract_protocol_name,extract_indexed_protocol_name,extract_indexed_message_name,make_protocol_path,make_message_path,extract_protocol_path,extract_parent
from util.schemas import validate
from config import N

class ProtocolManager:
    def __init__(self,path):
        self.main=path
        self.attivi={}
        self.stopped=set()
        self.mailbox={}
        self.received=set()
        self.result=None

    def find_schema(self,messagepath):
        path=self.main
        params={}
        protocol_path=extract_protocol_path(messagepath)
        while path != protocol_path:
            protocol=PROTOCOLS.get(extract_protocol_name(path))
            subprotocols=protocol.get_subprotocols(params)
            for subname,the_params in subprotocols.items():
                subpath= make_protocol_path(path,subname)
                if protocol_path.startswith(subpath):
                    path=subpath
                    params=the_params
                    break
            else:
                return None
        protocol=PROTOCOLS.get(extract_protocol_name(path))
        messagename,by=extract_indexed_message_name(messagepath)
        return protocol.get_schema(messagename,by,params)


    def dispatch(self,message):
        if (not isinstance(message.get('messageid'),str) or
            not isinstance(message.get('from') ,int)):
                return
        messageid=f"{message.get('messageid')}_{message.get('from')}"
        protocol_path=extract_protocol_path(messageid)
        if messageid in self.received or protocol_path in self.stopped:
            return
        schema=self.find_schema(messageid)
        if validate(message.get("data"),schema):
            self.received.add(messageid)
            self.mailbox[messageid]=message.get("data")
            protocol_path=extract_protocol_path(messageid)
            if protocol_path in self.attivi:
                self.run_hook(protocol_path)

    def run_hook(self,path):
        protocol=self.attivi[path]
        messages=protocol.get_messages()
        for message in messages:
            for i in range(1,N+1):
                messagepath=make_message_path(path,message,sender=i)
                messagedata= self.mailbox.get(messagepath)
                if messagedata is not None:
                    self.mailbox.pop(messagepath)
                    message,by=extract_indexed_message_name(messagepath)
                    protocol.handle_message(message,by,messagedata)

    def start_protocol(self,path,params=None):
        if path in self.attivi or path in self.stopped:
            raise Exception(f"protocol {path} started twice")
        Protocollo=PROTOCOLS[extract_protocol_name(path)]
        self.attivi[path]=Protocollo(self,path,params)
        self.run_hook(path)

    def stop_protocol(self,path):
        if path in self.stopped:
            return
        self.stopped.add(path)
        self.attivi.pop(path,None)
        protocol_name=extract_protocol_name(path)
        protocol=PROTOCOLS[protocol_name]
        messages=protocol.get_messages()
        for message in messages:
            for i in range(1,N+1):
                messagepath=make_message_path(path,message,sender=i)
                self.mailbox.pop(messagepath,None)
                if messagepath in self.received:
                    self.received.remove(messagepath)

    def is_done(self):
        return self.result is not None

    def return_to_parent(self,path,result):
        protocol_name,index=extract_indexed_protocol_name(path)
        parent_path=extract_parent(path)
        if parent_path == "/":
            self.result=result
        else:
            parent= self.attivi.get(parent_path)
            if parent:
                parent.handle_subprotocol(protocol_name,index,result)
        





