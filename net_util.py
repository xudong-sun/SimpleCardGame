def get_msg(socket):
    '''
    generator。从socket中读取信息
    all_msg可能由多组信息合成，被@隔开
    '''
    while True:
        if socket is None:
            break
        try:
            all_msg = socket.recv(8192)
        except OSError:
            break
        
        all_msg = all_msg[1:]
    
        while len(all_msg) > 0:
            pos = all_msg.find(b'@')
            if pos != -1:
                yield all_msg[:pos]
                all_msg = all_msg[pos+1:]
            else:
                yield all_msg
                break
     
    raise StopIteration
