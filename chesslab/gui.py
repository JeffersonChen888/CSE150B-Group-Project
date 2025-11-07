
import tkinter as tk
from tkinter import ttk
from .board import Board, WHITE, BLACK
from .ai import random_agent, minimax_ai, alphabeta_ai
from .mode import is_ai_turn, is_human_turn
from .common.profiling import Timer

UNICODE={'wK':'\u2654','wQ':'\u2655','wR':'\u2656','wB':'\u2657','wN':'\u2658','wP':'\u2659',
         'bK':'\u265A','bQ':'\u265B','bR':'\u265C','bB':'\u265D','bN':'\u265E','bP':'\u265F'}
CELL=80
class App:
    def __init__(self, root):
        self.root=root; self.root.title('ChessLab')
        self.board=Board(); self.selected=None
        self.status=tk.StringVar(value='New game. White moves.')
        self.mode=tk.StringVar(value='Human vs AI')
        self.ai=tk.StringVar(value='AlphaBeta'); self.depth=tk.IntVar(value=3)
        self.info=tk.StringVar(value='Ready.')
        self.human_side='w'  # human plays White by default
        self.ai_busy=False
        self.ai_after_id=None
        self.paused=False
        self.stopped=False
        top=ttk.Frame(root, padding=6); top.pack(fill='x')
        ttk.Button(top,text='New',command=self.new).pack(side='left',padx=4)
        self.pause_btn=ttk.Button(top,text='Pause',command=self.toggle_pause); self.pause_btn.pack(side='left',padx=4)
        ttk.Button(top,text='Stop',command=self.stop_ai).pack(side='left',padx=4)
        ttk.Label(top,text='Mode:').pack(side='left'); ttk.Combobox(top,textvariable=self.mode,values=['Human vs Human','Human vs AI','AI vs AI'],state='readonly',width=16).pack(side='left',padx=6)
        ttk.Label(top,text='AI:').pack(side='left'); ttk.Combobox(top,textvariable=self.ai,values=['Random','Minimax','AlphaBeta'],state='readonly',width=10).pack(side='left',padx=6)
        ttk.Label(top,text='Depth:').pack(side='left'); ttk.Spinbox(top,from_=1,to=6,textvariable=self.depth,width=4).pack(side='left',padx=6)
        ttk.Label(top,textvariable=self.status).pack(side='right')
        self.canvas=tk.Canvas(root,width=8*CELL,height=8*CELL,bg='white'); self.canvas.pack(padx=8,pady=8)
        self.canvas.bind('<Button-1>', self.onclick)
        bottom=ttk.Frame(root,padding=6); bottom.pack(fill='x'); ttk.Label(bottom,textvariable=self.info).pack(side='left')
        self.draw();
        if not self.paused and not self.stopped:
            self.ai_after_id = root.after(150, self.maybe_ai_move)
    def new(self):
        self.board=Board(); self.selected=None; self.status.set('New game. White moves.'); self.info.set('Ready.');
        if self.ai_after_id is not None:
            try: self.root.after_cancel(self.ai_after_id)
            except Exception: pass
            self.ai_after_id=None
        self.ai_busy=False
        self.draw(); self.ai_after_id = self.root.after(100,self.maybe_ai_move)
    def draw(self):
        self.canvas.delete('all')
        for r in range(8):
            for c in range(8):
                x0,y0=c*CELL,r*CELL; x1,y1=x0+CELL,y0+CELL
                fill='#eee' if (r+c)%2==0 else '#88a'
                self.canvas.create_rectangle(x0,y0,x1,y1,fill=fill,outline='')
                pc=self.board.board[r][c]
                if pc: self.canvas.create_text((x0+x1)//2,(y0+y1)//2,text=UNICODE[pc],font=('Segoe UI Symbol',36))
        if self.selected:
            r,c=self.selected; self.canvas.create_rectangle(c*CELL,r*CELL,c*CELL+CELL,r*CELL+CELL,outline='yellow',width=3)
    def onclick(self,e):
        # Disallow any click action when it's not the human's turn or interaction is paused
        if not self.can_human_act():
            self.selected=None
            return
        c,r=e.x//CELL,e.y//CELL
        if self.selected is None:
            pc=self.board.piece_at(r,c)
            if pc and ((pc[0]=='w' and self.board.turn==WHITE) or (pc[0]=='b' and self.board.turn==BLACK)):
                self.selected=(r,c); self.draw()
        else:
            from .board import Move
            mv=Move(self.selected,(r,c))
            # Re-check turn just before executing move
            if not self.can_human_act():
                self.selected=None; self.draw(); return
            if (mv.src,mv.dst) in [(m.src,m.dst) for m in self.board.legal_moves()]:
                self.board.make(mv); self.selected=None; self.after_move()
            else:
                self.selected=None; self.draw()
    def game_over(self):
        return self.board.outcome() is not None

    def can_human_act(self):
        # human may act only when it's their turn, not paused/stopped, game alive, and AI not executing
        return (not self.game_over()) and (not self.paused) and (not self.stopped) and (not self.ai_busy) and is_human_turn(self.mode.get(), self.board.turn, self.human_side)

    
    def toggle_pause(self):
        if self.game_over(): return
        if self.paused:
            self.paused=False; self.stopped=False
            self.status.set('Resumed.')
            if self.ai_after_id is not None:
                try: self.root.after_cancel(self.ai_after_id)
                except Exception: pass
                self.ai_after_id=None
            self.pause_btn.configure(text='Pause')
            # kick AI loop if needed
            self.ai_after_id = self.root.after(50, self.maybe_ai_move)
        else:
            self.paused=True
            self.status.set('Paused.')
            self.pause_btn.configure(text='Resume')

    def stop_ai(self):
        self.stopped=True; self.paused=False
        if self.ai_after_id is not None:
            try: self.root.after_cancel(self.ai_after_id)
            except Exception: pass
            self.ai_after_id=None
        self.status.set('Stopped.')
    
    def after_move(self):
        oc=self.board.outcome()
        if oc:
            kind,winner=oc
            self.status.set('Checkmate. '+('White' if winner=='w' else 'Black')+' wins.' if kind=='checkmate' else 'Stalemate.')
        else:
            self.status.set(('White' if self.board.turn=='w' else 'Black')+' to move.');
            if not self.paused and not self.stopped:
                if self.ai_after_id is not None:
                    try: self.root.after_cancel(self.ai_after_id)
                    except Exception: pass
                    self.ai_after_id=None
                self.ai_after_id = self.root.after(50,self.maybe_ai_move)
        self.draw()
    def maybe_ai_move(self):
        if self.board.outcome(): return
        if self.paused or self.stopped: return
        if not is_ai_turn(self.mode.get(), self.board.turn, 'b'): return
        if self.ai_busy: return
        self.ai_busy=True
        if not is_ai_turn(self.mode.get(), self.board.turn, 'b'): return
        depth=int(self.depth.get()); algo=self.ai.get(); move=None; metrics={}
        with Timer('ai_ms', metrics):
            if algo=='Random': move = random_agent.choose_move(self.board)
            elif algo=='Minimax':
                move, nodes = minimax_ai.choose_move(self.board, depth=depth, metrics=metrics); metrics['nodes']=nodes
            else:
                move, nodes = alphabeta_ai.choose_move(self.board, depth=depth, metrics=metrics); metrics['nodes']=nodes
        try:
            if move:
                self.board.make(move); self.info.set(f"AI {algo} d={depth} time={metrics.get('ai_ms',0):.1f}ms nodes={metrics.get('nodes',0)}"); self.after_move()
        finally:
            self.ai_busy=False

def main():
    root=tk.Tk(); App(root); root.mainloop()

if __name__=='__main__': main()
