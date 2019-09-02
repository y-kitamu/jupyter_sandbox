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

## Defining Confidence Weights : $\left\{ c_i(p) \right\}$
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

## Finding Consistency Weights : $\left\{ w_i \right\}_{i = 1}^{K}$

次のステップでは、consistency weights $\left\{w_i \right\}_{i = 1}^K$ を決定する。
ねじれが小さくなるようなものの重みを大きくして、ねじれが大きくなるようなものの重みを 0 にしたい。

### Objective Function
次の目的関数を最大化するように、$\boldsymbol{w} = \left\{ w_i \right\}_{i=1}^{K}$。

$$
    E_{M_1} (\boldsymbol{w}) = \sum_{i=1}^K \sum_{j=1}^K w_i w_j \int_{p \in M_1} S_{i,j}(p) c_i(p) c_j(p) dA(p) \\
    \mathrm{subject to} \ \ \sum_{i=1}^K w_i^2 = 1
$$

$c_i, c_j$ は confidence value、$S_{i, j}(p) : M_1 \to \mathbb{R}$ は２つの対応関係の一貫性を表す。
ここでは、投影した点同士の距離 (geodesic distance) の逆相関として、次のように定義する。

$$
S_{i,j} (p) = \exp \left( - \frac{d_{M_2}(m_i(p), m_j(p))}{\sigma^2} \right)
$$

多様体上では次のように変形すると効率的に $S_{i, j}$ を計算できる。

$$
S_{i,j} (p) = \exp \left( - \frac{d_{M_1} (p, m_i^{-1}(m_j(p)))}{\sigma^2} \right)
$$


### Optimizing for map consistency weights

上の最適化問題を解く方法を考える。
次のような行列 $\boldsymbol{S}$ を考える。

$$
    \boldsymbol{S}_{i, j} = \int_{M_1} c_i(p) c_j(p) S_{i,j}(p) dA(p)
$$

すると、最適化問題は次のように書ける。

$$
E_{M_1} (\boldsymbol{w}) = \boldsymbol{w}^T \boldsymbol{S} \boldsymbol{w}, \ \ s.t. \ \ \mid\mid \boldsymbol{w} \mid\mid_2 = 1
$$

$S$ は対称行列なので、最大固有値の固有ベクトルが最適解になる。
(Perron-Frobenius の定理から最適解 $\boldsymbol{w}$ はすべての要素で一定の符号を持つので、正の値を選ぶことができる。)

このようにして、最適解が計算できるが、２つの問題がある。
- 行列 $\boldsymbol{S}$ が大きくなってしまうこと
- near-isometry な解の候補が２つ以上存在する場合

#### Computing the Blending Matrix

$S$ の計算コストは高い。
$S$ はスパースな行列になる。
$S$ のある要素が 0 に近い値をとるかは、簡単に調べることができる。
conformal map を計算する 3 点のうち 2 点が共通していて、残りの１点が、同じ点が異なる点に移動していないものを選択して、計算する。

#### Processing Eigenvectors
大きい固有値をとる固有ベクトルが複数存在する場合がある。
このときは、inconsistent な対応関係が混ざることを避けるために、
次のようなステップで consistent weight vector $\boldsymbol{w}_1, ,,,, \boldsymbol{w}_n$ を計算する。

まず、最大固有値の 75 ％以上の固有値を持つ固有ベクトルを選ぶ。
次に、consistent weight vector $\boldsymbol{w}_1, ,,,, \boldsymbol{w}_n$ を構築する。
conformal map を $G_1, ,,,, G_n$ のグループに分割する。
固有ベクトルの要素の値の大きい順に上位 25 ％の conformal map を選ぶ。
まず最初の conformal map を $G_1$ に追加する。
conflict がないかを確認して、ない場合は $G_1$ にある場合は,次の $G_2$ に追加していく。
$\boldsymbol{w}$ の各要素に $\{0, 1\}$ の重み付けをして、conflict な map を取り除く。

このようにして作成した各 $w$ を用いて、最終的な blend map を生成する。
このとき、

$$
    f = \mathrm{arg}\min_{\{f_j\}_{j = 1}^n} \int_{M_1} c_{f_j} (p) dA(p)
$$

が最小になるような、$w$ を選ぶ。

