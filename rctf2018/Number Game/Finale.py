import string    
import hashlib
from itertools import product
import socket
import re
import solver


def connect(sock):
    data = sock.recv(1024).decode()
    sock.recv(1024).decode()
    hsh = data.replace('\n', '').split(' == ')[1]
    target = data.split('(')[1].split(')')[0].replace('+', '')
    answ = brute_force(target, hsh, verbose=True).encode()
    sock.send(answ[:4])

    
def solve_round(sock):
    game = solver.Game()
    while not game.is_finished():
        question = game.get_question()
        game.get_step()
        sock.send((' '.join(str(question)).encode()))
        answer = sock.recv(1024).decode()
        print(answer)
        if 'got it' in answer:
            return
        answer = tuple([int(i) for i in re.findall(r'[0-9]+', answer)]) 
        game.put_answer(answer)
    if game.is_correct():
        guessed = game.guessed_number()
        sock.send((' '.join(str(guessed)).encode()))
        print(sock.recv(1024))
        game.get_step()
       
    
def brute_force(mask, hsh, alphabet=string.ascii_letters+string.digits, verbose=False):
    pwd_pat = mask.replace('{', '{{').replace('}','}}').replace('*', '{}')
    N = mask.count('*')
    i = 0
    for chars in product(alphabet, repeat=N):
        if verbose:
            i += 1
            if i % 1000000 == 0:
                print('Iterations: {}'.format(i))
        if hsh == hashlib.sha256(pwd_pat.format(*chars).encode()).hexdigest():
            return pwd_pat.format(*chars)
    return None


sock = socket.socket()
sock.connect(('149.28.139.172', 10002))    
connect(sock)
sock.recv(10240) # receive MOTD
while 1:
    round = sock.recv(1024).decode()
    print(round)  # receive round numb
    solve_round(sock)
    if 'rctf' in round.lower():
        break
    