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

Sharpe = (rolling_mean/rolling_std)*sqrt(252) # the fact that we multiply it by sqrt of 252 is a beautiful statistical logic. annualization.

rolling_drawdown is just the equity/rolling_peak - 1

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



Then came CAGR, Calmar Ratio, and Sortino Ratio


Sortino ratio is better at punishing the negative standard deviations. Cause people don't really complain about a strategy if a stock has upward volatility lol.
the formula = rolling_mean/negative_returns_std

Calmar Ratio, is kind of weird really. It's like, the average returns you could get compared to the amount of struggle you'd have to go through via the strategy. 

CAGR, Compound Annual Growth Rate, is just (end_price/start_price)**(1/n) where n is number of years we're calculating over.

Calmar = CAGR/abs(drawdown)

You could say, it's basically letting you decide whether the risk to reward ratio is worth it, but it's like, lowkey similar to sharpe ratio yet different from sharpe ratio. It's just another perspective of looking at what Sharpe ratio is telling you about.
