"""Bounded math expressions; no Python attribute access or imports."""
import ast,math
_FUNCS={n:getattr(math,n) for n in ['sin','cos','tan','asin','acos','atan','atan2','sqrt','exp','log','floor','ceil','fabs']}
_FUNCS.update(abs=abs,min=min,max=max,pi=math.pi,e=math.e)
_CACHE={}
def power(a,b):
    if abs(float(b))>16 or abs(float(a))>1e6:raise ValueError('Power is outside formula limits')
    return float(a)**float(b)
class Powers(ast.NodeTransformer):
    def visit_BinOp(self,node):
        self.generic_visit(node)
        return ast.copy_location(ast.Call(func=ast.Name(id='_power',ctx=ast.Load()),args=[node.left,node.right],keywords=[]),node) if isinstance(node.op,ast.Pow) else node

def evaluate(text,**values):
    if len(text)>2048:raise ValueError('Formula exceeds 2048 characters')
    code=_CACHE.get(text)
    if code is None:
        tree=ast.parse(text,mode='eval');nodes=list(ast.walk(tree))
        allowed=(ast.Expression,ast.Constant,ast.Name,ast.Load,ast.BinOp,ast.UnaryOp,ast.Add,ast.Sub,ast.Mult,ast.Div,ast.Mod,ast.Pow,ast.USub,ast.UAdd,ast.Call,ast.Compare,ast.Lt,ast.LtE,ast.Gt,ast.GtE,ast.Eq,ast.NotEq,ast.IfExp,ast.BoolOp,ast.And,ast.Or)
        if len(nodes)>256 or any(not isinstance(n,allowed) for n in nodes):raise ValueError('Only scalar math expressions are supported')
        for n in nodes:
            if isinstance(n,ast.Call) and (not isinstance(n.func,ast.Name) or n.func.id not in _FUNCS):raise ValueError('Unsupported formula function')
            if isinstance(n,ast.Constant) and (not isinstance(n.value,(int,float)) or abs(n.value)>1e9):raise ValueError('Invalid formula constant')
        code=compile(ast.fix_missing_locations(Powers().visit(tree)),'CW formula','eval')
        if len(_CACHE)>256:_CACHE.clear()
        _CACHE[text]=code
    env=dict(_FUNCS);env.update(values);env['_power']=power
    value=float(eval(code,{'__builtins__':{}},env))
    if not math.isfinite(value) or abs(value)>1e9:raise ValueError('Formula result outside finite range')
    return value
