Proposed rule: Progressive Victory Threshold

Keeping the existing full-pattern victory condition. Add a second way to win that activates gradually as the match gets longer.
For a pattern requiring \(N\) squares, let \(k\) be the number currently occupied by a player's pawns.
Define the required number of occupied squares as:

\[
R(t)=
\begin{cases}
N & t < 160\\
\lceil 0.80N\rceil & 160\leq t<240\\
\lceil 0.65N\rceil & 240\leq t<320\\
\lceil 0.50N\rceil & t\geq320
\end{cases}
\]

A player wins when \(k\geq R(t)\), checked after their move.