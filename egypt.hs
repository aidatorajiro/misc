data Inverses = Inverse Integer | TOT

egyptDiv :: Integer -> Integer -> (Integer, [Integer])
egyptDiv m n =
    let doubles = takeWhile (<= m) $ iterate (*2) n
        choices = foldr (\inp def@(pre_i, pre_l) ->
                let nex_i = pre_i - inp
                 in if 0 <= nex_i then (nex_i, inp : pre_l)
                    else def
            ) (m, []) doubles
    in choices

main :: IO ()
main = do
    str1 <- getLine
    str2 <- getLine
    print (egyptDiv (read str1) (read str2))