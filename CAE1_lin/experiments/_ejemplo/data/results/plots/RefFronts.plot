set terminal wxt
set title 'Pareto Fronts'
set xlabel 'Objective 1'
set ylabel 'Objective 2'
set yrange [*:*]
set grid
set key top right

plot '../RefFront-Exp1.txt' with linespoints title 'Exp 1', '../RefFront-Exp2.txt' with linespoints title 'Exp 2', '../RefFront-Exp3.txt' with linespoints title 'Exp 3', '../RefFront-Exp4.txt' with linespoints title 'Exp 4', '../RefFront-Exp5.txt' with linespoints title 'Exp 5'

pause -1 'Press Enter to continue'
