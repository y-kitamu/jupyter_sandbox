# Blended Intrinsic Maps
Kim, Vladimir G., Yaron Lipman, and Thomas Funkhouser. 
"Blended intrinsic maps." ACM Transactions on Graphics (TOG). Vol. 30. No. 4. ACM, 2011.

## Abstract 
この論文の contribution は以下の通り
- blend maps の手法を提案。
- 滑らかな blending weight を定義
- area preservation と、他の点の対応関係との一貫性を保つように対応関係を選択する、global optimization problem を解いた

## Key Idea
次の式を最小化する。

$$
f(p) = \mathrm{arg}\min_{p' \in M_2} \sum_{i = 1}^K b_i(p)d_{M_2} (p', m_i(p))^2
$$

$\left\{ m_i(p) \right\}_{i = 1}^K : M_1 \to M_2$ は $K$ 個の対応関係の候補、 $b_{i}(p)$ は blending weight で、$d_{M_2}(\cdot, \cdot)$ は $M_2$ 上での geodesic distance (多様体?上の距離。2次元の場合は 2 点間の距離)である。
この式は各点 $p$ で $\left\{ m_i(p) \right\}_{i = 1}^K$ の重み付きの重心を求めることを意味している。
対応関係 $\left\{ m_i(p) \right\}$ と重み $b_{i}(p)$ が連続 (smooth) であるならば、blended map も連続であることが保証される。

この式を計算するには、候補となる対応関係 (candidate maps) を自動で生成する手法を提供することが必要になる。

conformal map (等角写像) は次元が低いので効率的に探索ができる。
conformal map は角度を保存するので shear による歪みを避けられる。
conformal map は非剛体の変形を表す一般的な対応関係 (map) である。
conformal map を用いることで、解析的にある点での歪み (distortion) を推定できるようになるので、 blending weight の計算が簡単になる。

blending weight を２つのファクターの積として表す
$$
b_i(p) = c_i(p) \cdot w_i(p)
$$
$c_i(p)$ は点 $p$ での conformal map $m_i$ の信頼度 (confidence) を表し、area preservation をもとに計算される。
$w_i(p)$ は、どの程度までその対応関係 (maps )を blending に用いていいかを示す、一貫性 (consistency) を表す。
$c_i(p)$ はすでに連続で変化する歪みの推定を提供していて、空間的に変化する $b_i(p)$ の模様を捉えている。
なので、$w_i(p)$ は surface を通して一定であるとして扱うことができ、最適な blending weight を計算するのを簡単にする。

## Generating Maps: $\left\{ m_i \right\}_{i = 1}^K$

ここでのゴールは、各特徴点ですくなくとも一つの対応関係 (map) は distortion が小さくなっているような対応関係のセットを求めることである。

そのような対応関係のセットを求めるために [Lipman nad Funkhouser 2009; Kim et al. 2010] の手法を用いる。
まず、特徴点 $P_1 \subset M_1, \ P_2 \subset M_2$ を計算する。その後、候補となる対応関係を triplet の対応関係を列挙することで生成する。この triplet の対応関係によって固有のメビウス変換が求められる。

### Generating feature points
まずはじめに特徴点のセット $P_1, P_2$ を生成する。
ここでのゴールは、対応関係の大部分を表すことができる、少数の特徴点を抽出することである。
今回は Average Geodesic Distance function 
$$
AGD_{M_l}(p) = \int_{M_l} d_g(p, p') dA(p')
$$
が最大になるように点を抽出する。$dA$ は surface $M_l$ ($l = 1, 2$) の面積分を表す。
https://dsp.stackexchange.com/questions/54826/what-is-different-between-euclidean-distance-and-the-geodesic-distance
今回紹介する例ではほとんどの場合で $\mid P_l \mid \le 10$ となっている。

### Generating conformal maps
特徴点を週出したら、対応関係の候補 (candidate maps) $\left\{ m_i \right\}_{i = 1}^K$ を作成する。
まず、[Lipman and Funkhouser 2009] に従い、mid-edge uniformization を使って２つの表面 (surface) を 
extended complex plane に conformally に写す。(これによって、3d の多様体上の点を 2d に投影でき、効率的に計算ができる。)
そして、$P_1, P_2$ の３点間の対応関係をすべて列挙して、
conformal map のセット $\left\{m_i \right\}_{i = 1}^K$ を生成する。
$K = _{\mid P_1 \mid}C_3 \cdot _{\mid P_2 \mid}C_3 \cdot 6$ となる。

## Defining COnfidence Weights : $\left\{ c_i(p) \right\}$
次のステップでは confidence value $c_i(p)$ を計算する。
distortion の計算方法には様々なものが考えられるが、ここでは、isometyr からの乖離を推定する。

conformal map は角度を保存するので、単に各 map のスケールファクターを計算することで、
isometry からの乖離を推定できる。
そこで、次のように $c_i(p)$ を定義する。
$$
c_i(p) = 2\left/ \left[ \frac{area(N_p)}{area(m_i(N_p))} + \frac{area(m_i(N_p))}{area(N_p)}  \right] \right. 
$$
ただし、$area(N_p)$ は点 $p$ の近傍の $M_1$ での面積で、$area(m_i(N_p))$ は $M_2$ での面積である。
計算の効率性のために $c_i(p)$ の計算に用いる点群として 256 点の等間隔に分布した点群 $P_{even}$ を用いる。
[Eldar et al. 1997]

## Finding COnsistency Weights : $\left\{ w_i \right\}_{i = 1}^{K}$
