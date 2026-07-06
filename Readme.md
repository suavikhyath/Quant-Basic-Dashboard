Well.

Things I learnt:
The most basic thing, i learnt what an equity curve is.
I had no idea what a Rolling Sharpe or a Drawdown Dashboard is.


Drawdown : basically a peak-to-trough decline magnitude? In my words at least.
Quants care about drawdown. A lot.

This is where my project started taking shape.

The dashboard is not asking:

"Did the strategy make money?"


It's asking:

"How much pain did investors endure while making that money?"



Next problem i came across: Drawdown being calculated for 15-20 years is absolute haywire.

So instead we do something called rolling. Very simple concept i just didn't know it was called rolling. It's basically a moving average type thing.


For every day:

Look back 252 trading days
(~1 year)

and compute:

Maximum Drawdown
Sharpe Ratio
Sortino Ratio


I realised that the beauty of returns lies in the fact that they're dimensionless.


This project gave more direction to the intuition of 'non-normal distribution' of return prices i had built from the last project.

standard deviation made much more sense when directly linked to volatility



Key insight I got worth sharing:
In my dashboard, equity curve went up and up.

BUT

rolling sharpe

was steadily falling.

What did that suggest?

The strategy was still making money.

But every unit of return now requires more risk than before.




Realized a cheeky little detail that portfolio growth follows compounding.

