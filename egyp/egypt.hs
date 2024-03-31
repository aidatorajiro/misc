data Inverses = Inverse Integer | TOT deriving Show

egyptDivU :: Integer -> Integer -> (Integer, [Integer])
egyptDivU m n =
    let doubles = takeWhile (<= m) $ iterate (*2) n
        choices = foldr (\inp def@(pre_i, pre_l) ->
                let nex_i = pre_i - inp
                 in if 0 <= nex_i then (nex_i, inp : pre_l)
                    else def
            ) (m, []) doubles
    in choices

--egyptDivL :: Integer -> Integer -> [Inverses]
--egyptDivL m n = 
--    let 
--    in snd 

main :: IO ()
main = do
    str1 <- getLine
    str2 <- getLine
    print (egyptDivU (read str1) (read str2))