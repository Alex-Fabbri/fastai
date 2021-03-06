import pytest, torch, fastai
from fastai.gen_doc.doctest import this_tests
from fastai.torch_core import *
from fastai.layers import *
from math import isclose

a=[1,2,3]
exp=torch.tensor(a)
b=[3,6,6]

def test_tensor_with_list():
    this_tests(tensor)
    r = tensor(a)
    assert torch.all(r==exp)

def test_tensor_with_ndarray():
    this_tests(tensor)
    b=np.array(a, dtype=np.int64)
    r = tensor(b)
    assert np_address(r.numpy()) == np_address(b)
    assert torch.all(r==exp)

def test_tensor_with_tensor():
    this_tests(tensor)
    c=torch.tensor(a)
    r = tensor(c)
    assert r.data_ptr()==c.data_ptr()
    assert torch.all(r==exp)

def test_requires_grad():
    this_tests(requires_grad)
    m = simple_cnn(b)
    assert requires_grad(m) == True

def test_requires_grad_set():
    this_tests(requires_grad)
    m = simple_cnn(b)
    requires_grad(m,False)
    allF = np.all([not p.requires_grad for p in m.parameters()])
    assert allF, "requires_grad(m,False) did not set all parameters to False"
    requires_grad(m,True)
    allT = np.all([p.requires_grad for p in m.parameters()])
    assert allT, "requires_grad(m,True) did not set all parameters to True"

def test_apply_init():
    this_tests(apply_leaf, apply_init)
    m = simple_cnn(b,bn=True)
    all2 = lambda m: nn.init.constant_(m.weight,0.2) if hasattr(m, 'weight') else m
    all7 = lambda m: nn.init.constant_(m,0.7)
    apply_leaf(m,all2)
    apply_init(m,all7)
    conv1_w = torch.full([6,3,3,3],0.7)
    bn1_w = torch.full([6],0.2)
    assert conv1_w.equal(m[0][0].weight), "Expected first colvulition layer's weights to be %r" % conv1_w
    assert bn1_w.equal(m[0][2].weight), "Expected first batch norm layers weights to be %r" % bn1_w

def test_in_channels():
    this_tests(in_channels)
    m = simple_cnn(b)
    assert in_channels(m) == 3

def test_in_channels_no_weights():
    this_tests(in_channels)
    with pytest.raises(Exception) as e_info:
        in_channels(nn.Sequential())
    assert e_info.value.args[0] == 'No weight layer'

def test_range_children():
    this_tests(range_children)
    m = simple_cnn(b)
    assert len(range_children(m)) == 3

def test_split_model():
    this_tests(split_model)
    m = simple_cnn(b)
    pool = split_model(m,[m[2][0]])[1][0]
    assert pool == m[2][0], "Did not properly split at adaptive pooling layer"

def test_split_no_wd_params():
    this_tests(split_no_wd_params)
    groups = split_no_wd_params(simple_cnn((1, 1, 1), bn=True))
    assert len(groups[0]) == 1
    assert len(groups[1]) == 2

def test_set_bn_eval():
    this_tests(set_bn_eval)
    m = simple_cnn(b,bn=True)
    requires_grad(m,False)
    set_bn_eval(m)
    assert m[0][2].training == False, "Batch norm layer not properly set to eval mode"

def test_np2model_tensor():
    this_tests(np2model_tensor)
    a = np.ones([2,2])
    t = np2model_tensor(a)
    assert isinstance(t,torch.FloatTensor)

def test_model_type(): 
    this_tests(model_type) 
    a=np.array([1.,2.,3.]).dtype 
    b=np.array([1,2,3]).dtype 
    c=np.array(["1","2","3"]).dtype 
    assert model_type(a) == torch.float32 
    assert model_type(b) == torch.int64 
    assert model_type(c) == None   
    
def test_trange_of():
    this_tests(trange_of)
    t = trange_of(a)
    assert len(t) == len(a)
    
def test_to_np():
    this_tests(to_np)
    a = to_np(exp)
    assert isinstance(a,np.ndarray)

def test_none_reduce_on_cpu():
    this_tests(NoneReduceOnCPU)
    y_pred = torch.ones([3,8], requires_grad=True)
    y_true = torch.zeros([3],dtype=torch.long)
    with NoneReduceOnCPU(nn.CrossEntropyLoss()) as lf:
        loss = lf(y_pred,y_true)
        assert isclose(loss.sum(),6.23,abs_tol=1e-2), "final loss does not seem to be correct"
    with NoneReduceOnCPU(F.cross_entropy) as lf:
        loss = lf(y_pred,y_true)
        assert isclose(loss.sum(),6.23,abs_tol=1e-2), "final loss without reduction does not seem to be correct"

def test_tensor_array_monkey_patch():
    this_tests('na')
    t = torch.ones(a)
    t = np.array(t)
    assert np.all(t == t), "Tensors did not properly convert to numpy arrays"
    t = torch.ones(a)
    t = np.array(t,dtype=float)
    assert np.all(t == t), "Tensors did not properly convert to numpy arrays with a dtype set"

def test_keep_parameter():
    sa = SelfAttention(128)
    this_tests(SelfAttention)
    flat = nn.Sequential(*flatten_model(sa))
    for p in sa.parameters(): assert id(p) in [id(a) for a in flat.parameters()]
