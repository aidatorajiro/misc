import Data.List ( zipWith6 )
import Data.Ratio ( (%) )

declining :: Int -> Int -> [Int]
declining k n = map (\x -> max (k-x) 0) [0..(n-1)]

laserCut :: [[Int]] -> Int -> [([Int],[Int],[Int])]
laserCut l s =
    let n = length l
        (n0, n2) = (declining s n, declining (n - s - 1) n)
        total = reverse [1..n]
        n1 = zipWith3 (\x y z -> z - x - y) n0 n2 total
        ls = zipWith3 (\x y z ->
            let (r0, r12) = splitAt y x
                (r1, r2 ) = splitAt z r12
             in (r0, r1, r2)) l n0 n1
     in ls

expand :: [[Int]] -> Int -> [[Int]]
expand l s =
    let n = length l
        (g0, g1, g2) = unzip3 $ laserCut l s
        c = zipWith6 (\x y z x' y' z' ->
            let supply = (case y of
                    [] -> [1]
                    _ -> [])
            in x ++
            (case x' of
                [] -> supply
                _ -> [last x' + head y']
            ) ++ y ++
            (case z' of
                [] -> supply
                _ -> [last y' + head z']
            ) ++ z)
            (g0++[[]]) ([]:g1) (g2++[[]]) ([]:g0) (g1++[[]]) ([]:g2)
     in c

-- expands [[1,1,1],[2,4],[7]] [....]

expands :: [[Int]] -> [Int] -> [[Int]]
expands = foldl expand

solveFor :: [[Int]] -> [[Int]] -> [Int]
solveFor a b = []

a = 0.4

b = a/(2.0::Double)

c = b

makeTex :: [[Int]] -> String
makeTex = concat . zipWith (\i -> concat . zipWith (
        \j n -> "\\draw (" ++ show (j * a + i * b) ++ "," ++ show (-i * a) ++ ") node {" ++ show n ++ "};"
    ) [0..]) [0..]

makeLines :: Int -> Int -> String
makeLines n z = let
        z' = fromIntegral z
        h' = fromIntegral (n - z - 1)
        [a0, a1, a2, a3, b0, b1, b2, b3] = map show [
            a * z',
            c,
            z' * b - c,
            - a * z',
            a * z',
            c,
            z' * a + h' * b + c,
            - h' * a]
    in "\\draw (" ++ a0 ++ ", " ++ a1 ++ ") -- (" ++ a2 ++ ", " ++ a3 ++ ");\\draw (" ++ b0 ++ ", " ++ b1 ++ ") -- (" ++ b2 ++ ", " ++ b3 ++ ");"

expandsTex :: [[Int]] -> [Int] -> [String]
expandsTex l s = reverse . snd $ foldl (\(x, y:ys) z -> let e = expand x z in (e, makeTex e : (y ++ makeLines (length x) z) : ys)) (l, [makeTex l]) s

makeMinipages :: Double -> [String] -> [String]
makeMinipages d = map (\x ->
    "\\begin{minipage}{"
    ++ show d ++
    "\\textwidth}\\begin{center}\\begin{tikzpicture}"
    ++ x ++
    "\\end{tikzpicture}\\end{center}\\end{minipage}")

toRational :: [Integer] -> Rational
toRational = foldr (\x y -> 1 / ((x % 1) - y)) 0

main :: IO ()
main = do
    putStrLn (concatMap (++"\n") $ makeMinipages 0.3 (expandsTex [[1,1,1],[2,4],[7]] [1,2,1,1,2,3]))
    putStrLn (concatMap (++"\n") $ makeMinipages 0.3 (expandsTex [[1,1,1],[2,4],[7]] [1,2,1,1,2,3,4,3,2,4,4,5,4,6,2,9,3,2,2,3,1,5,6,3,4,5,5,5,3,2,11,14,14,11,12,1,1,9,5,3]))
