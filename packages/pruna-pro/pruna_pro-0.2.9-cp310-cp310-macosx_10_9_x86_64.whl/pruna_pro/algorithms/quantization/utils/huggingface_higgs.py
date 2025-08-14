# Copyright 2024 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

from enum import Enum
from math import ceil, sqrt
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Type, Union

from pruna.engine.model_checks import is_causal_lm
from pruna.logging.logger import pruna_logger
from transformers.quantizers.base import HfQuantizer
from transformers.quantizers.quantizers_utils import get_module_from_name
from transformers.utils import is_torch_available
from transformers.utils.logging import tqdm
from transformers.utils.quantization_config import QuantizationConfigMixin

"""
HIGGS through FLUTE (Flexible Lookup Table Engine for LUT-quantized LLMs) integration file
"""

if TYPE_CHECKING:
    from transformers.modeling_utils import PreTrainedModel

if is_torch_available():
    import torch
    from torch import nn


def pad_to_block(tensor: torch.Tensor, dims: List[int], had_block_size: int, value: int = 0) -> torch.Tensor:
    """
    Pad a tensor to a multiple of had_block_size along specified dimensions.

    Parameters
    ----------
    tensor : torch.Tensor
        The input tensor to pad.
    dims : List[int]
        The dimensions along which to pad.
    had_block_size : int
        The block size to pad up to (will pad to next multiple of this value).
    value : int or float, optional
        The value to use for padding, by default 0.

    Returns
    -------
    torch.Tensor
        The padded tensor where specified dimensions are padded to multiples of had_block_size.
    """
    pad_dims = [0 for _ in range(2 * len(tensor.shape))]
    for dim in dims:
        size = tensor.shape[dim]
        next_multiple_of_1024 = ((size - 1) // had_block_size + 1) * had_block_size
        delta = next_multiple_of_1024 - size
        pad_dims[-2 * dim - 1] = delta

    return nn.functional.pad(tensor, pad_dims, "constant", value)


def get_higgs_grid(p: int, n: int) -> torch.Tensor:
    """
    Get the Higgs grid (ie gaussian optimal codebook in dimension p).

    Parameters
    ----------
    p : int
        The number of dimensions.
    n : int
        The number of elements in each dimension.

    Returns
    -------
    torch.Tensor
        The Higgs grid.
    """
    if (p, n) == (2, 256):
        return torch.tensor(
            [
                [-2.501467704772949, 0.17954708635807037],
                [-0.6761789321899414, 1.2728623151779175],
                [-1.8025816679000854, 0.7613157629966736],
                [-0.538287878036499, -2.6028504371643066],
                [0.8415029644966125, -0.8600977659225464],
                [0.7023013234138489, 3.3138747215270996],
                [0.5699077844619751, 2.5782253742218018],
                [3.292393207550049, -0.6016128063201904],
                [0.5561617016792297, -1.7723814249038696],
                [-2.1012380123138428, 0.020958125591278076],
                [0.46085724234580994, 0.8428705334663391],
                [1.4548040628433228, -0.6156039237976074],
                [3.210029363632202, 0.3546904921531677],
                [0.8893890976905823, -0.5967988967895508],
                [0.8618854284286499, -3.2061192989349365],
                [1.1360996961593628, -0.23852407932281494],
                [1.6646337509155273, -0.9265465140342712],
                [1.4767773151397705, 1.2476022243499756],
                [-1.0511897802352905, 1.94503915309906],
                [-1.56318998336792, -0.3264186680316925],
                [-0.1829211413860321, 0.2922491431236267],
                [-0.8950616717338562, -1.3887052536010742],
                [-0.08206957578659058, -1.329533576965332],
                [-0.487422913312912, 1.4817842245101929],
                [-1.6769757270812988, -2.8269758224487305],
                [-1.5057679414749146, 1.8905963897705078],
                [1.8335362672805786, 1.0515104532241821],
                [0.3273945450782776, 1.0491033792495728],
                [-3.295924186706543, -0.7021600008010864],
                [-1.8428784608840942, -1.2315762042999268],
                [-0.8575026392936707, -1.7005949020385742],
                [-1.120667815208435, 0.6467998027801514],
                [-0.1588846743106842, -1.804071068763733],
                [-0.8539647459983826, 0.5645008683204651],
                [-1.4192019701004028, -0.6175029873847961],
                [1.0799058675765991, 1.7871345281600952],
                [1.171311855316162, 0.7511613965034485],
                [2.162078380584717, 0.8044339418411255],
                [1.3969420194625854, -1.243762493133545],
                [-0.23818807303905487, 0.053944624960422516],
                [2.304199457168579, -1.2667627334594727],
                [1.4225027561187744, 0.568610668182373],
                [0.376836895942688, -0.7134661674499512],
                [2.0404467582702637, 0.4087389409542084],
                [0.7639489769935608, -1.1367933750152588],
                [0.3622530400753021, -1.4827953577041626],
                [0.4100743532180786, 0.36108437180519104],
                [-1.5867475271224976, -1.618212342262268],
                [-2.2769672870635986, -1.2132309675216675],
                [0.9184022545814514, -0.34428009390830994],
                [-0.3902314603328705, 0.21785245835781097],
                [3.120687484741211, 1.3077973127365112],
                [1.587440848350525, -1.6506884098052979],
                [-1.718808889389038, -0.038405973464250565],
                [-0.6888407468795776, -0.8402308821678162],
                [-0.7981445789337158, -1.1117373704910278],
                [-2.4124443531036377, 1.3419722318649292],
                [-0.6611530184745789, 0.9939885139465332],
                [-0.33103418350219727, -0.16702833771705627],
                [-2.4091389179229736, -2.326857566833496],
                [1.6610108613967896, -2.159703254699707],
                [0.014884627424180508, 0.3887578248977661],
                [0.029668325558304787, 1.8786455392837524],
                [1.180362582206726, 2.699317216873169],
                [1.821286678314209, -0.5960053205490112],
                [-0.44835323095321655, 3.327436685562134],
                [-0.3714401423931122, -2.1466753482818604],
                [-1.1103475093841553, -2.4536871910095215],
                [-0.39110705256462097, 0.6670510172843933],
                [0.474752813577652, -1.1959707736968994],
                [-0.013110585510730743, -2.52519154548645],
                [-2.0836575031280518, -1.703289270401001],
                [-1.1077687740325928, -0.1252644956111908],
                [-0.4138077199459076, 1.1837692260742188],
                [-1.977599024772644, 1.688241720199585],
                [-1.659559965133667, -2.1387736797332764],
                [0.03242531046271324, 0.6526556015014648],
                [0.9127950072288513, 0.6099498867988586],
                [-0.38478314876556396, 0.433487206697464],
                [0.27454206347465515, -0.27719801664352417],
                [0.10388526320457458, 2.2812814712524414],
                [-0.014394169673323631, -3.177137613296509],
                [-1.2871228456497192, -0.8961855173110962],
                [0.5720916986465454, -0.921597957611084],
                [1.1159656047821045, -0.7609877586364746],
                [2.4383342266082764, -2.2983546257019043],
                [-0.294057160615921, -0.9770799875259399],
                [-0.9342701435089111, 1.107579231262207],
                [-1.549338698387146, 3.090520143508911],
                [2.6076579093933105, 2.051239013671875],
                [-0.9259037375450134, 1.407211184501648],
                [-0.1747353971004486, 0.540488600730896],
                [-0.8963701725006104, 0.8271111249923706],
                [0.6480194926261902, 1.0128909349441528],
                [0.980783998966217, -0.06156221032142639],
                [-0.16883476078510284, 1.0601658821105957],
                [0.5839992761611938, 0.004697148688137531],
                [-0.34228450059890747, -1.2423977851867676],
                [2.500824451446533, 0.3665279746055603],
                [-0.17641609907150269, 1.3529551029205322],
                [0.05378641560673714, 2.817232847213745],
                [-1.2391047477722168, 2.354328155517578],
                [0.630434513092041, -0.668536365032196],
                [1.7576488256454468, 0.6738647818565369],
                [0.4435231387615204, 0.6000469326972961],
                [-0.08794835954904556, -0.11511358618736267],
                [1.6540337800979614, 0.33995017409324646],
                [-0.04202975332736969, -0.5375117063522339],
                [-0.4247745871543884, -0.7897617220878601],
                [0.06695003807544708, 1.2000739574432373],
                [-3.2508881092071533, 0.28734830021858215],
                [-1.613816261291504, 0.4944162368774414],
                [1.3598989248275757, 0.26117825508117676],
                [2.308382511138916, 1.3462618589401245],
                [-1.2137469053268433, -1.9254342317581177],
                [-0.4889402985572815, 1.8136259317398071],
                [-0.1870335340499878, -0.3480615019798279],
                [1.0766386985778809, -1.0627082586288452],
                [0.4651014506816864, 2.131748914718628],
                [-0.1306295394897461, -0.7811847925186157],
                [0.06433182954788208, -1.5397958755493164],
                [-0.2894323468208313, -0.5789554715156555],
                [-0.6081662178039551, 0.4845278263092041],
                [2.697964668273926, -0.18515698611736298],
                [0.1277363896369934, -0.7221432328224182],
                [0.8700758218765259, 0.35042452812194824],
                [0.22088994085788727, 0.495242178440094],
                [-2.5843818187713623, -0.8000828623771667],
                [0.6732649803161621, -1.4362232685089111],
                [-1.5286413431167603, 1.0417330265045166],
                [-1.1222513914108276, -0.6269875764846802],
                [-0.9752035140991211, -0.8750635385513306],
                [-2.6369473934173584, 0.6918523907661438],
                [0.14478731155395508, -0.041986867785453796],
                [-1.5629483461380005, 1.4369450807571411],
                [0.38952457904815674, -2.16428804397583],
                [-0.16885095834732056, 0.7976621985435486],
                [-3.12416934967041, 1.256506085395813],
                [0.6843105554580688, -0.4203019142150879],
                [1.9345275163650513, 1.934950351715088],
                [0.012184220366179943, -2.1080918312072754],
                [-0.6350273489952087, 0.7358828186988831],
                [-0.837304949760437, -0.6214472651481628],
                [0.08211923390626907, -0.9472538232803345],
                [2.9332995414733887, -1.4956780672073364],
                [1.3806978464126587, -0.2916182279586792],
                [0.06773144006729126, 0.9285762310028076],
                [-1.1943119764328003, 1.5963770151138306],
                [1.6395620107650757, -0.32285431027412415],
                [-1.390851378440857, -0.08273141086101532],
                [1.816330909729004, -1.2812227010726929],
                [0.7921574711799622, -2.1135804653167725],
                [0.5817914605140686, 1.2644577026367188],
                [1.929347038269043, -0.2386285960674286],
                [0.8877345323562622, 1.190008521080017],
                [1.4732073545455933, 0.8935023546218872],
                [-2.8518524169921875, -1.5478795766830444],
                [0.2439267635345459, 0.7576767802238464],
                [0.5246709585189819, -2.606659412384033],
                [1.150876760482788, 1.4073830842971802],
                [-0.2643202245235443, 2.0634236335754395],
                [1.555483341217041, -0.0023102816194295883],
                [2.0830578804016113, -1.7225427627563477],
                [-0.5424830317497253, -1.070199728012085],
                [0.9168899655342102, 0.8955540060997009],
                [-0.8120972514152527, 2.696739912033081],
                [-0.29908373951911926, -1.5310651063919067],
                [1.2320337295532227, -1.556247353553772],
                [1.8612544536590576, 0.08704725652933121],
                [0.22133447229862213, -1.8091708421707153],
                [-0.4403655230998993, -0.38571012020111084],
                [-1.88539457321167, 1.192205786705017],
                [2.239687919616699, 0.004709010478109121],
                [1.139495611190796, 0.45733731985092163],
                [-1.507995367050171, 0.19716016948223114],
                [0.46986445784568787, 1.5422041416168213],
                [-1.2573751211166382, -0.35984551906585693],
                [-1.7415345907211304, -0.6020717024803162],
                [1.0751984119415283, 0.19006384909152985],
                [2.24186635017395, -0.46343153715133667],
                [0.3610347509384155, -0.07658443599939346],
                [-1.3111497163772583, 0.432013601064682],
                [0.6164408326148987, 0.24538464844226837],
                [-1.9266542196273804, -0.3256155550479889],
                [-0.5870336890220642, -0.1879584938287735],
                [-1.0476511716842651, 0.3677721917629242],
                [-1.229940414428711, 1.2433830499649048],
                [0.18550436198711395, 0.22753673791885376],
                [-0.017921989783644676, 0.12625974416732788],
                [1.1659504175186157, -0.5020995736122131],
                [-0.5983408093452454, -1.40438973903656],
                [0.7519024014472961, -0.16282692551612854],
                [0.9920787811279297, -1.344896912574768],
                [-0.8103678226470947, 0.3064485788345337],
                [0.6956969499588013, 1.8208192586898804],
                [-2.7830491065979004, -0.2299390584230423],
                [-0.34681546688079834, 2.4890666007995605],
                [-1.4452646970748901, -1.2216600179672241],
                [-2.1872897148132324, 0.8926076292991638],
                [1.706072211265564, -2.8440372943878174],
                [1.1119003295898438, -2.4923460483551025],
                [-2.582794666290283, 2.0973289012908936],
                [0.04987720400094986, -0.2964983284473419],
                [-2.063807487487793, -0.7847916483879089],
                [-0.4068813621997833, 0.9135897755622864],
                [-0.9814359545707703, -0.3874954879283905],
                [-1.4227229356765747, 0.7337291240692139],
                [0.3065044581890106, 1.3125417232513428],
                [1.2160996198654175, -1.9643305540084839],
                [-1.2163853645324707, 0.14608727395534515],
                [-2.3030710220336914, -0.37558120489120483],
                [0.9232977628707886, 2.1843791007995605],
                [-0.1989777386188507, 1.651851773262024],
                [-0.714374840259552, -0.39365994930267334],
                [-0.7805715799331665, -2.099881887435913],
                [0.9015759229660034, -1.7053706645965576],
                [0.1033422127366066, 1.5256654024124146],
                [-1.8773194551467896, 2.324174165725708],
                [1.9227174520492554, 2.7441604137420654],
                [-0.5994020104408264, 0.23984014987945557],
                [1.3496100902557373, -0.9126054644584656],
                [-0.8765304088592529, -3.1877026557922363],
                [-1.2040035724639893, -1.5169521570205688],
                [1.4261796474456787, 2.150200128555298],
                [1.463774561882019, 1.6656692028045654],
                [0.20364105701446533, -0.4988172650337219],
                [0.5195154547691345, -0.24067887663841248],
                [-1.1116786003112793, -1.1599653959274292],
                [-0.8490808606147766, -0.1681060940027237],
                [0.3189965784549713, -0.9641751646995544],
                [-0.5664751529693604, -0.5951744318008423],
                [-1.6347930431365967, -0.9137664437294006],
                [0.44048091769218445, -0.47259435057640076],
                [-2.147747039794922, 0.47442489862442017],
                [1.834734320640564, 1.4462147951126099],
                [1.1777573823928833, 1.0659226179122925],
                [-0.9568989872932434, 0.09495053440332413],
                [-1.838529348373413, 0.2950586676597595],
                [-0.4800611734390259, 0.014894310384988785],
                [-0.5235516428947449, -1.7687653303146362],
                [2.0735011100769043, -0.8825281262397766],
                [2.637502431869507, 0.8455678224563599],
                [2.606602907180786, -0.7848446369171143],
                [-1.1886937618255615, 0.9330510497093201],
                [0.38082656264305115, 0.13328030705451965],
                [0.6847941875457764, 0.7384101152420044],
                [1.2638574838638306, -0.007309418171644211],
                [0.18292222917079926, -1.22371244430542],
                [0.8143821954727173, 1.4976691007614136],
                [0.6571850776672363, 0.48368802666664124],
                [-0.6991601586341858, 2.150190830230713],
                [0.8101756572723389, 0.10206498205661774],
                [-0.08768226951360703, -1.084917664527893],
                [-0.7208092212677002, 0.03657956421375275],
                [0.3211449086666107, 1.803687334060669],
                [-0.7835946083068848, 1.6869111061096191],
            ]
        )
    if (p, n) == (2, 64):
        return torch.tensor(
            [
                [-2.7216711044311523, 0.14431366324424744],
                [-0.766914427280426, 1.7193410396575928],
                [-2.2575762271881104, 1.2476624250411987],
                [1.233758807182312, -2.3560616970062256],
                [0.8701965808868408, -0.2649352252483368],
                [1.4506438970565796, 2.1776366233825684],
                [-0.06305818259716034, 1.9049758911132812],
                [2.536226511001587, 0.563927412033081],
                [0.4599496126174927, -1.8745561838150024],
                [-1.900517225265503, -0.30703988671302795],
                [0.09386251866817474, 0.8755807280540466],
                [1.946500539779663, -0.6743080615997314],
                [2.1338934898376465, 1.4581491947174072],
                [0.9429940581321716, -0.8038390278816223],
                [2.0697755813598633, -1.614896535873413],
                [0.772676408290863, 0.22017823159694672],
                [1.0689979791641235, -1.525044322013855],
                [0.6813604831695557, 1.1345642805099487],
                [0.4706456661224365, 2.606626272201538],
                [-1.294018030166626, -0.4372096061706543],
                [-0.09134224057197571, 0.4610418677330017],
                [-0.7907772064208984, -0.48412787914276123],
                [0.060459110885858536, -0.9172890186309814],
                [-0.5855047702789307, 2.56172513961792],
                [0.11484206467866898, -2.659848213195801],
                [-1.5893300771713257, 2.188580274581909],
                [1.6750942468643188, 0.7089915871620178],
                [-0.445697546005249, 0.7452405095100403],
                [-1.8539940118789673, -1.8377939462661743],
                [-1.5791912078857422, -1.017285943031311],
                [-1.030419945716858, -1.5746369361877441],
                [-1.9511750936508179, 0.43696075677871704],
                [-0.3446580767631531, -1.8953213691711426],
                [-1.4219647645950317, 0.7676230669021606],
                [-0.9191089272499084, 0.5021472573280334],
                [0.20464491844177246, 1.3684605360031128],
                [0.5402919054031372, 0.6699410676956177],
                [1.8903915882110596, 0.03638288006186485],
                [0.4723062515258789, -0.6216739416122437],
                [-0.41345009207725525, -0.22752176225185394],
                [2.7119064331054688, -0.5111885070800781],
                [1.065286636352539, 0.6950305700302124],
                [0.40629103779792786, -0.14339995384216309],
                [1.2815024852752686, 0.17108257114887238],
                [0.01785222627222538, -0.43778058886528015],
                [0.054590027779340744, -1.4225547313690186],
                [0.3076786696910858, 0.30697619915008545],
                [-0.9498570561408997, -0.9576997756958008],
                [-2.4640724658966064, -0.9660449028015137],
                [1.3714425563812256, -0.39760473370552063],
                [-0.4857747256755829, 0.2386789172887802],
                [1.2797833681106567, 1.3097363710403442],
                [0.5508887767791748, -1.1777795553207397],
                [-1.384316325187683, 0.1465839296579361],
                [-0.46556955575942993, -1.2442727088928223],
                [-0.3915477693080902, -0.7319604158401489],
                [-1.4005504846572876, 1.3890998363494873],
                [-0.8647305965423584, 1.0617644786834717],
                [-0.8901953101158142, -0.01650036871433258],
                [-0.9893633723258972, -2.4662880897521973],
                [1.445534110069275, -1.049334168434143],
                [-0.041650623083114624, 0.012734669260680676],
                [-0.3302375078201294, 1.26217782497406],
                [0.6934980154037476, 1.7714335918426514],
            ]
        )
    elif (p, n) == (2, 16):
        return torch.tensor(
            [
                [-0.8996632695198059, -1.6360418796539307],
                [-0.961183488368988, 1.5999565124511719],
                [-1.882026195526123, 0.678778350353241],
                [0.36300793290138245, -1.9667866230010986],
                [-0.6814072728157043, -0.576818585395813],
                [0.7270012497901917, 0.6186859607696533],
                [0.3359416127204895, 1.8371193408966064],
                [1.859930396080017, 0.036668598651885986],
                [0.17208248376846313, -0.9401724338531494],
                [-1.7599700689315796, -0.6244229674339294],
                [-0.8993809223175049, 0.32267823815345764],
                [0.839488685131073, -0.3017036020755768],
                [1.5314953327178955, 1.2942044734954834],
                [-0.0011779458727687597, 0.00022069070837460458],
                [1.4274526834487915, -1.207889199256897],
                [-0.16123905777931213, 0.8787511587142944],
            ]
        )
    elif (p, n) == (1, 16):
        return torch.tensor(
            [
                [-2.7325894832611084],
                [-2.069017171859741],
                [-1.6180464029312134],
                [-1.2562311887741089],
                [-0.9423404335975647],
                [-0.6567591428756714],
                [-0.38804829120635986],
                [-0.12839503586292267],
                [0.12839503586292267],
                [0.38804829120635986],
                [0.6567591428756714],
                [0.9423404335975647],
                [1.2562311887741089],
                [1.6180464029312134],
                [2.069017171859741],
                [2.7325894832611084],
            ]
        )
    elif (p, n) == (1, 8):
        return torch.tensor(
            [
                [-2.1519455909729004],
                [-1.3439092636108398],
                [-0.7560052871704102],
                [-0.2450941801071167],
                [0.2450941801071167],
                [0.7560052871704102],
                [1.3439092636108398],
                [2.1519455909729004],
            ]
        )
    elif (p, n) == (1, 4):
        return torch.tensor([[-1.5104175806045532], [-0.4527800381183624], [0.4527800381183624], [1.5104175806045532]])
    else:
        raise NotImplementedError(f"Unsupported p={p}, n={n}")


def quantize_with_higgs(
    weight: torch.Tensor,
    bits: int = 4,
    p: int = 2,
    group_size: int = 256,
    hadamard_size: int = 1024,
    example_batch_size: int = 1,
    imported_modules: Dict[str, Any] = dict(),
) -> Dict[str, torch.Tensor]:
    """
    Quantize a weight matrix using the HIGGS algorithm.

    Parameters
    ----------
    weight : torch.Tensor
        The weight matrix to quantize. Must be 2-dimensional.
    bits : int, optional
        Number of bits to use for quantization, by default 4. Must be 2, 3 or 4.
    p : int, optional
        Number of dimensions for the codebook, by default 2. Must be 1 or 2.
    group_size : int, optional
        Size of groups for quantization, by default 256. Must be 64, 128 or 256.
    hadamard_size : int, optional
        Size of Hadamard transform blocks, by default 1024. Must be divisible by group_size.
    example_batch_size : int, optional
        Batch size for inference with the HIGGS-quantized model. Default is 1.
    imported_modules : Dict[str, Any], optional
        The isolated imported modules.

    Returns
    -------
    Dict[str, torch.Tensor]
        Dictionary containing:
        - weight: Quantized weight tensor
        - scales: Scaling factors
        - tables: Lookup tables for FLUTE
        - tables2: Additional lookup tables for FLUTE
        - tune_metadata: Module-wise metadata for saving the kernel tuning results, including:
            - gemm block shapes
            - GPU metadata
            - other tuning parameters
    """
    assert len(weight.shape) == 2, "Only 2D weights are supported for now"

    grid = get_higgs_grid(p, 2 ** (p * bits)).to(weight.device)
    grid_norm_2 = torch.linalg.norm(grid, axis=-1) ** 2

    device = weight.device
    dtype = weight.dtype
    weight = weight.clone().float()
    # Pad to Hadamard transform size
    weight = pad_to_block(weight, [1], hadamard_size)

    # Scale and Hadamard transform
    mult = weight.shape[1] // hadamard_size
    weight = weight.reshape(-1, mult, hadamard_size)
    scales = torch.linalg.norm(weight, axis=-1)
    weight = imported_modules["hadamard_transform"](weight, 1) / scales[:, :, None]

    # Pad to edenn_d and project
    weight = pad_to_block(weight, [2], p).reshape(weight.shape[0], mult, -1, p)

    # Quantize
    codes = torch.empty(weight.shape[:-1], device=device, dtype=torch.uint8)
    for i in range(0, weight.shape[0], 16):
        codes[i : i + 16] = torch.argmax(2 * weight[i : i + 16] @ grid.T - grid_norm_2, dim=-1).to(torch.uint8)
    del weight

    codes = codes.reshape(codes.shape[0], -1)
    scales = scales / sqrt(hadamard_size)

    weight, scales, tables, tables2, tune_metadata = imported_modules["prepare_data_transposed"](
        codes,
        torch.repeat_interleave(scales.to(dtype), hadamard_size // group_size, dim=1),
        grid.to(dtype),
        num_bits=bits,
        group_size=group_size,
        vector_size=p,
        dtype=dtype,
        device=device,
        example_batch_size=example_batch_size,
    )

    return {
        "weight": weight,
        "scales": scales,
        "tables": tables,
        "tables2": tables2.view(dtype=torch.float16),
        "tune_metadata": tune_metadata,
    }


class HiggsLinear(torch.nn.Module):
    """
    Linear layer implementation using HIGGS quantization.

    Parameters
    ----------
    in_features : int
        Size of each input sample.
    out_features : int
        Size of each output sample.
    num_bits : int
        Number of bits to use for quantization.
    bias : bool, optional
        If True, adds a learnable bias to the output, by default True.
    dtype : torch.dtype, optional
        The dtype of the layer, by default None.
    device : torch.device, optional
        The device to put the layer on, by default None.
    group_size : int, optional
        Size of groups for quantization, by default 256.
    hadamard_size : int, optional
        Size of Hadamard transform blocks, by default 1024.
    imported_modules : Dict[str, Any], optional
        The isolated imported modules.
    """

    def __init__(
        self,
        in_features: int,
        out_features: int,
        num_bits: int,
        bias: bool = True,
        dtype: torch.dtype = torch.float16,
        device: torch.device = torch.device("cuda"),
        group_size: int = 256,
        hadamard_size: int = 1024,
        imported_modules: Dict[str, Any] = dict(),
    ) -> None:
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.num_bits = num_bits
        self.group_size = group_size
        self.hadamard_size = hadamard_size

        assert in_features % group_size == 0
        assert num_bits in [2, 3, 4]

        self.weight = nn.Parameter(
            torch.empty((out_features * num_bits // 16, in_features), dtype=torch.int16, device=device),
            requires_grad=False,
        )
        self.scales = nn.Parameter(
            torch.empty((out_features, in_features // group_size), dtype=dtype, device=device), requires_grad=False
        )
        self.tables = nn.Parameter(torch.empty((2**num_bits,), dtype=dtype, device=device), requires_grad=False)
        self.tables2 = nn.Parameter(
            torch.empty((2**num_bits, 2**num_bits, 2), dtype=dtype, device=device), requires_grad=False
        )

        if bias:
            self.bias = nn.Parameter(torch.empty(out_features, device=device, dtype=dtype), requires_grad=False)
        else:
            self.register_parameter("bias", None)

        self.workspace = None  # must be set externally to be reused among layers
        self.tune_metadata = None  # must be set externally because architecture dependent
        self.qgemm_v2 = imported_modules["qgemm_v2"]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass of the HiggsLinear layer with flute CUDA kernel.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor.

        Returns
        -------
        torch.Tensor
            Output tensor after applying the quantized linear transformation.
        """
        x = pad_to_block(x, [-1], self.hadamard_size)

        if self.workspace is None:
            raise Exception("Workspace must be set before calling forward")

        return self.qgemm_v2(
            x,
            self.weight,
            self.scales,
            self.tables,
            self.tables2.view(dtype=torch.float32),
            self.workspace,
            self.tune_metadata,
            hadamard_size=self.hadamard_size,
        )


def dequantize_higgs(
    model: "PreTrainedModel" | torch.nn.Module, current_key_name: Optional[List[str]] = None
) -> "PreTrainedModel" | torch.nn.Module:
    """
    Dequantize the HiggsLinear layers in the given model by replacing them with standard torch.nn.Linear layers.

    This function recursively traverses the model and replaces any HiggsLinear layers
    with equivalent torch.nn.Linear layers, preserving the weights and biases.

    Parameters
    ----------
    model : PreTrainedModel
        The model containing HiggsLinear layers to be dequantized.
    current_key_name : Optional[List[str]], optional
        A list to keep track of the current module names during recursion, by default None.

    Returns
    -------
    PreTrainedModel
        The model with HiggsLinear layers replaced by torch.nn.Linear layers.
    """
    with torch.no_grad():
        for name, module in model.named_children():
            if current_key_name is None:
                current_key_name = []
            current_key_name.append(name)

            if isinstance(module, HiggsLinear):
                in_features = module.in_features
                out_features = module.out_features

                linear = torch.nn.Linear(
                    in_features,
                    out_features,
                    bias=module.bias is not None,
                    device=module.scales.device,
                    dtype=module.scales.dtype,
                )

                linear.weight.data = module(
                    torch.eye(in_features, device=module.scales.device, dtype=module.scales.dtype)
                ).T.contiguous()

                model._modules[name] = linear

            if len(list(module.children())) > 0:
                _ = dequantize_higgs(
                    module,
                    current_key_name=current_key_name,
                )
            # Remove the last key for recursion
            current_key_name.pop(-1)
        return model


class QuantizationMethod(str, Enum):
    """
    Enumeration of supported quantization methods.

    Parameters
    ----------
    value : Any
        Enum value.
    names : list
        List of enum names.
    module : str
        Module name.
    qualname : str
        Qualified name.
    type : type
        Base type for enum.
    start : int
        Starting value.
    """

    HIGGS = "higgs"


class HiggsConfig(QuantizationConfigMixin):
    """
    HiggsConfig is a configuration class for quantization using the HIGGS algorithm.

    Parameters
    ----------
    bits : int, optional
        Number of bits to use for quantization. Can be 2, 3 or 4. Default is 4.
    p : int, optional
        Quantization grid dimension. 1 and 2 are supported.
        2 is always better in practice. Default is 2.
    modules_to_not_convert : list, optional
        List of linear layers that should not be quantized. Default is ["lm_head"].
    hadamard_size : int, optional
        Hadamard size for the HIGGS algorithm. Default is 512. Input dimension of
        matrices is padded to this value. Decreasing this below 512 will reduce
        the quality of the quantization.
    group_size : int, optional
        Group size for the HIGGS algorithm. Can be 64, 128 or 256.
        Decreasing it barely affects the performance. Default is 256.
        Must be a divisor of hadamard_size.
    example_batch_size : int, optional
        Batch size for inference with the HIGGS-quantized model. Default is 1.
    tune_metadata : Optional[Dict[str, Any]], optional
        Module-wise metadata (gemm block shapes, GPU metadata, etc.) for saving the kernel tuning
        results. Default is an empty dictionary. Is set automatically during tuning.
    **kwargs : dict
        Additional arguments passed to parent class.
    """

    def __init__(
        self,
        bits: int = 4,
        p: int = 2,
        modules_to_not_convert: Optional[List[str]] = None,
        hadamard_size: int = 512,
        group_size: int = 256,
        example_batch_size: int = 1,
        tune_metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        if modules_to_not_convert is None:
            modules_to_not_convert = ["lm_head"]
        if tune_metadata is None:
            tune_metadata = {}

        self.quant_method = QuantizationMethod.HIGGS  # type: ignore
        self.bits = bits
        self.p = p
        self.modules_to_not_convert = modules_to_not_convert
        self.hadamard_size = hadamard_size
        self.group_size = group_size
        self.example_batch_size = example_batch_size
        self.tune_metadata = tune_metadata
        self.post_init()

    def post_init(self) -> None:
        """
        Safety checker that arguments are correct - also replaces some NoneType arguments with their default values.

        Raises
        ------
        AssertionError
            If any of the arguments have invalid values.
        """
        assert self.bits in [2, 3, 4], "bits must be 2, 3 or 4"
        assert self.p in [1, 2], "p must be 1 or 2. 2 is always better in practice"
        assert self.group_size in [64, 128, 256], "group_size must be 64, 128 or 256"
        assert self.hadamard_size % self.group_size == 0, "hadamard_size must be divisible by group_size"
        assert self.example_batch_size in [1, 2, 4, 8, 16], "example_batch_size must be 1, 2, 4, 8 or 16"

    def to_diff_dict(self) -> Dict[str, Any]:
        """
        Patch for diffusers config to be serializable.

        Returns
        -------
        Dict[str, Any]
            Dictionary of all the attributes that make up this configuration instance.
        """
        return self.to_dict()


def get_num_sms_from_device(device: torch.device) -> int:
    """
    Get the number of streaming multiprocessors (SMs) for a given CUDA device.

    Parameters
    ----------
    device : torch.device
        The CUDA device to get the number of SMs for.

    Returns
    -------
    int
        The number of SMs for the device.

    Raises
    ------
    NotImplementedError
        If the device capability is not supported.
    """
    target_device_cc = torch.cuda.get_device_capability(device=device)
    if target_device_cc == (8, 6):
        return 84
    elif target_device_cc == (8, 0):
        return 108
    elif target_device_cc == (8, 9):
        return 128
    else:
        raise NotImplementedError(
            f"Device capability {target_device_cc} not supported for FLUTE (yet?) "
            "to verify your device capability check out https://developer.nvidia.com/cuda-gpus"
        )


def create_hf_quantizer_class(imported_modules: Dict[str, Any]) -> Type[HfQuantizer]:
    """
    Create a quantizer class for HIGGS quantization.

    Parameters
    ----------
    imported_modules : Dict[str, Any]
        The isolated imported modules.

    Returns
    -------
    Type[HfQuantizer]
        The quantizer class.
    """
    # before we create the quantizer class, we need to create the replace function
    replace_with_higgs_linear = create_replace_with_higgs_linear_function(imported_modules)

    class HiggsHfQuantizer(HfQuantizer):
        """
        HIGGS algorithm quantizer for loading prequantized models and in-flight quantization of full-precision models.

        Parameters
        ----------
        quantization_config : QuantizationConfigMixin
            Configuration for quantization.
        **kwargs : dict
            Additional arguments passed to parent class.
        """

        requires_calibration = False
        requires_parameters_quantization = True
        required_packages = ["flute-kernel", "fast_hadamard_transform"]  # type: ignore

        def __init__(self, quantization_config: QuantizationConfigMixin, **kwargs) -> None:
            super().__init__(quantization_config, **kwargs)
            self.quantization_config = quantization_config

        def validate_environment(self, device_map: Union[str, Dict[str, str]], **kwargs) -> None:
            """
            Validate the environment for HIGGS quantization.

            Parameters
            ----------
            device_map : Union[str, Dict]
                The device mapping for model placement.
            **kwargs : dict
                Additional keyword arguments.
            """
            # testing the installed packages should have already been done in our
            # import_method_packages in the PrunaQuantizer class.
            # So only remains to check device_map.

            if device_map is None:
                raise ValueError(
                    "You are attempting to load a HIGGS model without setting device_map."
                    " Please set device_map comprised of 'cuda' devices."
                )
            elif isinstance(device_map, dict) and ("cpu" in device_map.values() or "disk" in device_map.values()):
                raise ValueError(
                    "You are attempting to load a HIGGS model with a device_map that contains a CPU or disk device."
                    " This is not supported. Please remove the CPU or disk device from the device_map."
                )

        def update_torch_dtype(self, torch_dtype: "torch.dtype") -> "torch.dtype":
            """
            Update torch dtype for compatibility.

            Parameters
            ----------
            torch_dtype : torch.dtype
                The dtype to update.

            Returns
            -------
            torch.dtype
                The updated dtype.
            """
            if torch_dtype is None:
                pruna_logger.info("`torch_dtype` is None. Setting `torch_dtype=torch.float16` for FLUTE compatibility.")
                torch_dtype = torch.float16
            elif torch_dtype != torch.float16 and torch_dtype != torch.bfloat16:
                raise ValueError(
                    f"Invalid `torch_dtype` {torch_dtype}. HIGGS quantization only supports "
                    "`torch_dtype=torch.float16` or `torch_dtype=torch.bfloat16`."
                )

            return torch_dtype

        def create_quantized_param(  # type: ignore
            self,
            model: "PreTrainedModel",
            param_value: "torch.Tensor",
            param_name: str,
            target_device: "torch.device",
            state_dict: Dict[str, Any],
            unexpected_keys: Optional[List[str]] = None,
        ) -> None:
            """
            Quantize weights into weight and weight_scale.

            Parameters
            ----------
            model : PreTrainedModel
                The model to quantize.
            param_value : torch.Tensor
                The parameter value to quantize.
            param_name : str
                Name of the parameter.
            target_device : torch.device
                Target device for quantization.
            state_dict : Dict[str, Any]
                State dictionary of the model.
            unexpected_keys : Optional[List[str]], optional
                List of unexpected keys, by default None.
            """
            flute_dict = quantize_with_higgs(
                param_value.to(target_device),
                getattr(self.quantization_config, "bits"),
                getattr(self.quantization_config, "p"),
                getattr(self.quantization_config, "group_size"),
                getattr(self.quantization_config, "hadamard_size"),
                getattr(self.quantization_config, "example_batch_size"),
                imported_modules=imported_modules,
            )

            del param_value

            module, _ = get_module_from_name(model, param_name)
            module_name = ".".join(param_name.split(".")[:-1])
            for key, value in flute_dict.items():
                if key in module._parameters:
                    module._parameters[key] = torch.nn.Parameter(value, requires_grad=False)
                elif key in module._buffers:
                    module._buffers[key] = value  # torch.nn.Buffer(value)
                elif key == "tune_metadata":
                    module.tune_metadata = value
                    self.quantization_config.tune_metadata[module_name] = value.to_dict()  # type: ignore[attr-defined]
                else:
                    raise ValueError(f"Unexpected key {key} in module {module}")

            if unexpected_keys is not None and param_name in unexpected_keys:
                unexpected_keys.remove(param_name)

        def _process_model_before_weight_loading(
            self,
            model: "PreTrainedModel",
            **kwargs,
        ) -> None:
            replace_with_higgs_linear(
                model,
                quantization_config=self.quantization_config,
            )
            model.config.quantization_config = self.quantization_config

        def _process_model_after_weight_loading(self, model: "PreTrainedModel", **kwargs) -> None:
            flute_workspaces = {}
            flute_modules = {name: module for name, module in model.named_modules() if isinstance(module, HiggsLinear)}
            for name, module in tqdm(flute_modules.items(), desc="Repacking HIGGS modules", leave=False):
                # Every HiggsLinear needs a "workspace": a buffer for the unpacking operation.
                # This buffer needs to be on the same device as the weights, but can be reused across modules otherwise.
                if module.weight.device not in flute_workspaces:
                    flute_workspaces[module.weight.device] = imported_modules["make_workspace_streamk"](
                        device=module.weight.device
                    )
                module.workspace = flute_workspaces[module.weight.device]

                # FLUTE weights are packed in a way that is optimized for a specific number of SMs
                # (GPU streaming multiprocessors).
                # If the model is loaded on a different device than the one it was saved on,
                # we need to repack the weights.
                module.tune_metadata = imported_modules["TuneMetaData"].from_dict(
                    getattr(self.quantization_config, "tune_metadata")[name]
                )
                module.weight.data, module.tune_metadata = imported_modules["maybe_tune_and_repack"](
                    weight=module.weight.data,
                    scales=module.scales.data,
                    metadata=module.tune_metadata,
                    example_batch_size=getattr(self.quantization_config, "example_batch_size"),
                )
                self.quantization_config.tune_metadata[name] = module.tune_metadata.to_dict()  # type: ignore[attr-defined]

        def update_missing_keys(self, model: "PreTrainedModel", missing_keys: List[str], prefix: str) -> List[str]:
            """
            Update the list of missing keys.

            Parameters
            ----------
            model : PreTrainedModel
                The model to check.
            missing_keys : List[str]
                List of missing keys.
            prefix : str
                Prefix to check against.

            Returns
            -------
            List[str]
                Updated list of missing keys.
            """
            higgs_names = {name for name, module in model.named_modules() if isinstance(module, HiggsLinear)}

            def should_update(key: str) -> bool:
                if key.endswith(".weight") or key.endswith(".bias"):
                    return False
                full_key = f"{prefix}.{key}"
                return any(name in key or name in full_key for name in higgs_names)

            return [key for key in missing_keys if not should_update(key)]

        @property
        def is_trainable(self, model: Optional["PreTrainedModel"] = None) -> bool:
            """
            Check if the quantizer supports training.

            Parameters
            ----------
            model : Optional[PreTrainedModel], optional
                The model to check trainability for, by default None

            Returns
            -------
            bool
                Always returns False since HIGGS quantization does not support training
            """
            return False

        def is_serializable(self, safe_serialization: Optional[bool] = None) -> bool:
            """
            Check if the quantizer is serializable.

            Parameters
            ----------
            safe_serialization : bool, optional
                Whether to use safe serialization, by default None.

            Returns
            -------
            bool
                True if serializable, False otherwise.
            """
            return True

        def check_quantized_param(
            self,
            model: "PreTrainedModel",
            param_value: "torch.Tensor",
            param_name: str,
            state_dict: Dict[str, Any],
            **kwargs,
        ) -> bool:
            """
            Check if a parameter should be quantized.

            Parameters
            ----------
            model : PreTrainedModel
                The model containing the parameter.
            param_value : torch.Tensor
                The value of the parameter.
            param_name : str
                The name of the parameter.
            state_dict : Dict[str, Any]
                The state dictionary containing the parameter.
            **kwargs : dict
                Additional keyword arguments.

            Returns
            -------
            bool
                True if the parameter should be quantized, False otherwise.
            """
            module, tensor_name = get_module_from_name(model, param_name)
            # Only quantize weights of HiggsLinear modules that are not already quantized
            return isinstance(module, HiggsLinear) and tensor_name == "weight" and param_value.dtype != torch.int16

        def _dequantize(self, model: "PreTrainedModel") -> "PreTrainedModel":
            model = dequantize_higgs(model)  # type: ignore
            return model

    return HiggsHfQuantizer


def create_replace_with_higgs_linear_function(imported_modules: Dict[str, Any]) -> Callable:
    """
    Create a function that recursively replaces the Linear layers of the given model with HIGGS quantized layers.

    Parameters
    ----------
    imported_modules : Dict[str, Any]
        The isolated imported modules.

    Returns
    -------
    Callable
        The function that recursively replaces the Linear layers of the given model with HIGGS quantized layers.
    """

    def replace_with_higgs_linear(
        model: torch.nn.Module,
        quantization_config: "HiggsConfig",
        current_key_name: Optional[List[str]] = None,
        has_been_replaced: bool = False,
        layer_type: type[nn.Module] = HiggsLinear,
    ) -> tuple[torch.nn.Module, bool]:
        """
        Public method that recursively replaces the Linear layers of the given model with HIGGS quantized layers.

        `accelerate` is needed to use this method. Returns the converted model and a boolean that indicates if the
        conversion has been successfull or not.

        Parameters
        ----------
        model : torch.nn.Module
            The model to convert.
        quantization_config : HiggsConfig, optional
            The quantization configuration, by default None.
        current_key_name : List[str], optional
            Current key name for recursion, by default None.
        has_been_replaced : bool, optional
            Whether any layers have been replaced, by default False.
        layer_type : type[nn.Module], optional
            The type of layer to replace the Linear layers with, by default HiggsLinear.

        Returns
        -------
        Tuple[torch.nn.Module, bool]
            The converted model and whether any layers were replaced.
        """
        from accelerate import init_empty_weights  # type: ignore

        for name, module in model.named_children():
            if current_key_name is None:
                current_key_name = []
            current_key_name.append(name)

            if isinstance(module, nn.Linear):
                # Check if the current key is not in the `quantization_config.modules_to_not_convert`
                current_key_name_str = ".".join(current_key_name)
                if not any(current_key_name_str.endswith(key) for key in quantization_config.modules_to_not_convert):
                    with init_empty_weights():
                        in_features = module.in_features
                        out_features = module.out_features
                        new_module = layer_type(
                            in_features,
                            out_features,
                            bias=module.bias is not None,
                            num_bits=quantization_config.bits,
                            hadamard_size=quantization_config.hadamard_size,
                            group_size=quantization_config.group_size,
                            imported_modules=imported_modules,
                        )
                        # Store the module class in case we need to transpose the weight later
                        setattr(new_module, "source_cls", type(module))
                        # Force requires grad to False to avoid unexpected errors
                        for param in new_module.parameters():
                            param.requires_grad = False

                        model._modules[name] = new_module
                        has_been_replaced = True

            if len(list(module.children())) > 0:
                _, has_been_replaced = replace_with_higgs_linear(
                    module,
                    quantization_config=quantization_config,
                    current_key_name=current_key_name,
                    has_been_replaced=has_been_replaced,
                    layer_type=layer_type,
                )
            # Remove the last key for recursion
            current_key_name.pop(-1)
        return model, has_been_replaced

    return replace_with_higgs_linear


def get_modules_to_not_convert(
    model: "PreTrainedModel",
    weight_bits: int,
    device: torch.device,
    group_size: int,
    hadamard_size: int,
    percentage_to_not_convert: Optional[int] = 0,
) -> List[str]:
    """
    Get the modules that should not be converted to HIGGS quantized layers.

    Parameters
    ----------
    model : PreTrainedModel
        The model to get the modules to not convert.
    weight_bits : int
        The number of bits to use for the weights.
    device : torch.device
        The device to check the capability of.
    group_size : int
        The group size to use for the weights.
    hadamard_size : int
        The hadamard size to use for the weights.
    percentage_to_not_convert : int
        The percentage of modules that should not be converted to HIGGS quantized layers.

    Returns
    -------
    List[str]
        The modules that should not be converted to HIGGS quantized layers.
    """
    if is_causal_lm(model):
        # For LLMs, we should only avoid quantizing the last layer:
        modules_to_not_convert = ["lm_head"]
    else:
        # The following is valid, for now, only for Flux denoisers.
        # The first 8 layers of the transfomer_blocks are very sensitive to quantization,
        # maybe because they are the ones that are used for combining text and image embeddings?
        # single_transformer_blocks (used for image only) can be quantized.
        n_layers = min(model.config.num_layers, 8)
        n_single_layers = model.config.num_single_layers
        modules_to_not_convert_5percent = [
            "time_text_embed.text_embedder.linear_1",
            "time_text_embed.text_embedder.linear_2",
            "time_text_embed.time_step_embedder.linear_2",
            "norm_out.linear",
            "context_embedder",
        ] + [f"single_transformer_blocks.{i}.norm.linear" for i in range(n_single_layers)]
        modules_to_not_convert_10percent = (
            modules_to_not_convert_5percent
            + ["transformer_blocks." + str(i) + ".attn.to_q" for i in range(n_layers)]
            + ["transformer_blocks." + str(i) + ".attn.to_k" for i in range(n_layers)]
            + ["transformer_blocks." + str(i) + ".attn.to_v" for i in range(n_layers)]
        )
        modules_to_not_convert_15percent = (
            modules_to_not_convert_10percent
            + ["transformer_blocks." + str(i) + ".norm1.linear" for i in range(n_layers)]
            + ["transformer_blocks." + str(i) + ".norm1_context.linear" for i in range(n_layers)]
            + ["transformer_blocks." + str(i) + ".attn.to_out.0" for i in range(n_layers)]
            + ["transformer_blocks." + str(i) + ".attn.to_add_out" for i in range(n_layers)]
            + ["transformer_blocks." + str(i) + ".attn.to_out.0" for i in range(n_layers)]
        )
        modules_to_not_convert_20percent = (
            modules_to_not_convert_15percent
            + ["transformer_blocks." + str(i) + ".ff.net.0.proj" for i in range(n_layers)]
            + ["transformer_blocks." + str(i) + ".ff.net.2" for i in range(n_layers)]
            + ["transformer_blocks." + str(i) + ".ff_context.net.0.proj" for i in range(n_layers)]
            + ["transformer_blocks." + str(i) + ".ff_context.net.2" for i in range(n_layers)]
        )

        # The user can choose to quantize all layers, or to skip quantization
        # for 5%, 10%, 15%, or 20% of the layers.
        if percentage_to_not_convert == 0:
            modules_to_not_convert = []
        elif percentage_to_not_convert == 5:
            modules_to_not_convert = modules_to_not_convert_5percent
        elif percentage_to_not_convert == 10:
            modules_to_not_convert = modules_to_not_convert_10percent
        elif percentage_to_not_convert == 15:
            modules_to_not_convert = modules_to_not_convert_15percent
        elif percentage_to_not_convert == 20:
            modules_to_not_convert = modules_to_not_convert_20percent
        else:
            raise ValueError(f"Invalid percentage_to_not_convert value: {percentage_to_not_convert}")

    # We should also avoid quantizing the weights
    # that are too small for the kernels
    # cf https://github.com/PrunaAI/flute/blob/2d1e8fa7be0d6c7d72125963b34d593358533e9c/flute/utils.py#L320
    # This is not something the user can change, but a model/hardware limitation.
    # In FLUTE, the tiles are respectively of size 64 and 32.
    # 16 is the default number of bits used for representing the weights before quantization.
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Linear):
            if weight_bits == 3:
                output_tile_size = ceil(ceil(module.out_features / 16) / 32)
            else:
                output_tile_size = ceil(ceil(module.out_features / 16) / 32 * weight_bits)
            if (
                ceil(module.in_features / 64) * output_tile_size
                < torch.cuda.get_device_properties(device=device).multi_processor_count
            ):
                modules_to_not_convert.append(name)
                pruna_logger.debug(f"Not quantizing {name} because it is too small for the FLUTE cuda kernels")
            if module.in_features % group_size != 0 and name not in modules_to_not_convert:
                modules_to_not_convert.append(name)
                pruna_logger.debug(f"Not quantizing {name} because it is not a multiple of the group size")
            if module.out_features % 128 != 0 and name not in modules_to_not_convert:
                modules_to_not_convert.append(name)
                pruna_logger.debug(f"Not quantizing {name} because it is not a multiple of the chunk size")
            if module.in_features % hadamard_size != 0 and name not in modules_to_not_convert:
                modules_to_not_convert.append(name)
                pruna_logger.debug(f"Not quantizing {name} because it is not a multiple of the hadamard_size")
            # Skip quantization for modules with incompatible dimensions.
            # Future: Add padding to weights to handle non-multiple dimensions
    return modules_to_not_convert


def check_device_capability() -> None:
    """Check if the device has the necessary capability to run FLUTE kernels."""
    if torch.cuda.is_available():
        device_capability = torch.cuda.get_device_capability()
        if device_capability[0] < 8:  # Ampere architecture is 8.x
            pruna_logger.warning(
                "For running inference with the HIGGS algorithm, you need a GPU with "
                "Ampere architecture (RTX 30 series or newer). "
                "If your GPU architecture is older, you can still quantize the model with Higgs, "
                "but you need a newer GPU for inference."
            )
