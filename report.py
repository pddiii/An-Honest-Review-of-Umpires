# %%
import pandas as pd
from unidecode import unidecode

# load in the data
data = pd.read_csv('data/games.csv')

# columns which need to be of numeric type
numeric_cols = ['R [H]', 'R [A]', 'PC',
       'IC', 'xIC', 'CC', 'xCC', 'CCAx', 'Acc', 'xAcc', 'AAx', 'Con',
       'Fav [H]', 'totRI']

# transform the columns to numeric type
for col in numeric_cols:
    data[col] = pd.to_numeric(data[col], errors='coerce')
    
# remove accents from the 'Umpire' column and convert to lower case
data['Umpire'] = data['Umpire'].apply(lambda x: unidecode(str(x)).lower())

# print(data)

# %% [markdown]
# # An Honest Review of MLB Umpires
# 
# Today was a historic day in the MLB. Angel Hernandez has finally retired. Hernandez has had quite the career as an umpire, I can't say it was a great career but for sure it was historic. However I wanted to look further beneath the surface to see if there's any truth to him being the "worst" umpire in the MLB. I will utilize data sourced from the UmpScorecards project to assess who is objectively the worst umpire in the MLB.
# 
# # A note on UmpScorecards Methodology
# 
# For a better understanding of the UmpScorecards methodology here are some useful links to UmpScorecards resources:
# 
# - [Explainers](https://umpscorecards.com/info/#explainers)
# - [FAQs](https://umpscorecards.com/info/#faqs)
# - [Glossary](https://umpscorecards.com/info/#glossary)
# 
# 
# 
# # A Reflection on Notable Angel Hernandez blunders
# 
# As a Phillies fan, I have quite a few fond memories of him over the last 3 seasons. 
# 
# In April 2022, my favorite funny moment in baseball happened when Kyle Schwarber had a tantrum after a missed Angel Hernandez call. In a game against the Brewers when the Phillis were losing by 1 run in the bottom of the 9th Kyle Schwarber found himself in a full count. Josh Hader deals him a pitch low and outside which Hernandez incorrectly calls a ball. Hernandez had an incosistent strike zone all night, and Schwarber could not contain himself anymore. With 2 hands he overhead spikes his bat on the ground, then throws his helmet, and starts yelling at Hernandez. He points to both sides of the plate referring to the outside zone Hernandez had been missing the whole night. This resulted in Schwarber's ejection but it will forever be burned into my mind as an example of what makes people desire automated umpires. 
# 
# One I'll never forget is a confrontation with Bryce Harper from the 2023 season. It was 1-1 with a full count in the bottom of the 3rd against the Pittsburgh Pirates. Bryce is dealt a pitch low and out of the zone that he checks his swing on, and Angel Hernandez makes a notable blunder saying Bryce goes around. Harper lost his mind on Hernandez's terrible call, and was promptly ejected from the game as a result. 
# 
# # Cleaning the Data

# %%
# Calculate the sum of the specified columns grouped by 'Umpire'
sums = data.groupby('Umpire')[['PC', 'IC', 'xIC', 'CC', 'xCC']].sum().reset_index()

# Calculate the mean of the specified columns grouped by 'Umpire'
means = data.groupby('Umpire')[['CCAx', 'Acc', 'xAcc', 'AAx', 'Con', 'Fav [H]', 'totRI']].mean().reset_index()

# Calculate the counts of each umpire
counts = data['Umpire'].value_counts().reset_index()
counts.columns = ['Umpire', 'GC']

# Merge the sums, means and counts into a new DataFrame
summary = pd.merge(sums, means, on='Umpire')
summary = pd.merge(summary, counts, on='Umpire')

# Create a list of the columns in the dataframe
cols = summary.columns.tolist()
# Move the "GC" column next to the "Umpire" column
cols.insert(1, cols.pop(cols.index('GC')))
# Reorder the columns in the dataframe
summary = summary[cols].round(decimals=3)
# summary.to_csv('data/ump_totals.csv', index=False)

# print(summary)

# %% [markdown]
# # Angel Hernandez's Stats

# %%
angel = summary[summary['Umpire'] == 'angel hernandez']
# print(angel)

# %% [markdown]
# As we can see Angel Hernandez called over 247 games since the 2015 season, when UmpScorecards data begins, and this includes 34,592 pitches called in these games.
# 
# As a result I will arbitrarily constrict this to Umpires who have called within about 5,000 pitches less than Angel Hernandez, so we will use only umpires with $PC \geq 29,500$

# %%
# Filter the dataframe to only umpires with at least 30,000 pitches called
seasoned_umps = summary[summary['PC'] >= 29500].round(decimals=3).copy()
seasoned_umps.loc[:, 'IC_per_100'] = seasoned_umps['IC'] / 100

# Create and add columns with the percentile rankings of the specified columns
# sorted in ascending order (1 is best, 0 is worst)
for col in ['Acc', 'Con', 'AAx']:
    seasoned_umps.loc[:, col + '_pct'] = seasoned_umps[col].rank(ascending=True, pct=True)*100

# Create and add columns with the percentile rankings of the specified columns
# sorted in ascending order (1 is worst, 0 is best)
for col in ['IC_per_100', 'totRI']:
    seasoned_umps.loc[:, col + '_pct'] = seasoned_umps[col].rank(ascending=False, pct=True)*100

# Add a column with the average rank from the columns above
# the closer the 'avg_rank' is to 1 the better the umpire
seasoned_umps.loc[:, 'avg_pct'] = seasoned_umps.filter(regex='_pct$').mean(axis=1)
# Sort the dataframe by the average rank in descending order
seasoned_umps = seasoned_umps.sort_values('avg_pct', ascending=False).reset_index(drop=False)
# Add a column with the home team favor rank (a measure of bias in an umpires calls)
seasoned_umps.loc[:, 'Fav_pct'] = seasoned_umps['Fav [H]'].abs().rank(ascending=False, pct=True)*100
seasoned_umps = seasoned_umps.round(decimals=3)
# seasoned_umps.to_csv('data/seasoned_umps.csv', index=False)

# %% [markdown]
# # So how bad is Angel Hernandez truly?
# 
# The best part about Angel Hernandez's possibly forced retirement from umpiring is seeing the rejoice from the fans of Major League Baseball, yet the fairly opposite reactions of other umpires. The best example is of fellow bad umpire Joe West who commented on a radio talk show, "I know the lawyer that handled his case, and I know that when they went through everything that he was graded on, he was in the top 20 percent [of umpires]".
# 
# If I'm being honest I have no idea who is letting a lawyer speak on the matter of Umpire performance, that does not make any sense. I would love to know what the statisticians and data scientists who analyzed Hernandez's calls came to a conclusion on. Another thing that bothered me is Joe West's criticism of UmpScorecards and in general review of umpires calls utilizing technology after the game. West stated "I hate the fact that these people that sit behind a desk and get behind a computer and send out all these social media things, they don’t know what they’re talking about."
# 
# I find this funny because Joe West sounds like every other scared, low-performance umpire because after years of ineptitude technology is beginning to elucidate his flaws to the baseball community. I will continue to focus primarily on Joe West and Angel Hernandez from here on out.
# 
# Below is the full list of umpires ranked upon a few selected columns ranked using percentiles:
# 
# - In all of these rankings a value closer to 1 indicates better performance by the umpire, while values closer to 0 indicates worse performance.
# - The `avg_rank` column is an average of the other `_rank` columns with the exception of `Fav_rank`. This aims to measure overall performance of the umpires based on the average percentile of their rankings in the following categories:
#   - Accuracy (% of Correct Calls)
#   - Consistency
#   - AAx (Accuracy above Expected Accuracy)
#   - IC_per_100 (Incorrect Calls per 100 pitches called)
#   - totRI (total Run Impact)

# %%
# print(seasoned_umps.iloc[:, [1, 2] + list(range(15, seasoned_umps.shape[1] ) ) ] )

# %% [markdown]
# # The Angel and Joe Show

# %%
# Print out only Angel Hernandez and Joe West
angel_joe = seasoned_umps.iloc[[45, 51], [1, 2] + list(range(15, seasoned_umps.shape[1] ) )]
# print(angel_joe.round(decimals=3))

# %% [markdown]
# ## General Overview of their performance
# 
# As we can see from the above rankings Angel Hernandez and Joe West are low-performing umpires. To be clear, I'm utilizing the data available to the general public and this is not an opinion piece. From our rankings we are able to see that both of these umpires are in the bottom 20% of umpire performance.
# 
# Overall out of 56 MLB umpires with at least 29,500 Pitches Called (`PC`) since UmpScorecards data is available in 2015 MLB Season, Angel Hernandez and Joe West are the 46th and 52nd best performing MLB umpires respectively.
# 
# ## Discussing their Respectives Flaws
# 
# ### Angel Hernandez
# 
# Let's start with Angel Hernandez. Angel's worst traits when it comes to umpiring are his Consistency and his total Run Impact in the games he has umpired. He ranked in the 7th percentile for Consistency, and the 11th percentile for total Run Impact. These are both dreadful performances, and I believe these are the primary reasons why people were constantly on Hernandez's back and criticizing him more severely than other umpires.
# 
# Hernandez underperforms as an umpire but time and time again he does this in high leverage, and impactful situations within the games. As a fan this provides me a better understanding of why he's so widely disliked, recall the Phillies situations I mentioned earlier.
# 
# ### Joe West
# 
# As for Joe West, he is noticeably worst than Hernandez in every category with the exception of Consistency and incorrect calls per 100. The two statistics I want to highlight about West is that he is the 1st percentile for both Accuracy and total Run Impact. Since 2015, Joe West has been the least accurate umpire and the most negatively impactful umpire to terms in terms of runs. I don't believe there's much more needed to be said about Joe West to understand his poor performance.
# 
# ## Giving Credit where it's Due
# 
# I want to remark that the one thing I find statistically remarkable about Angel Hernandez during his umpiring career is that Hernandez ranks in the 95th percentile of umpires for the `Favor [H]` variable. This is good for 4th best amongst all umpires.
# 
# This variable measure the number of runs in favor of the home team where a positive value represents a benefit for the home team, while a negative value represents a benefit for the away team. The ranking was calculated using the absolute values of the `Fav [H]` column, where the closer a value is to 0 then the closer it's percentile is to 1.
# 
# I'm interested in this variable because despite Hernandez's lack of consistency and rather low accuracy on Pitch Calls he is usually hurting both teams about equally. While the impact of favor typically doesn't more than around 0.1 runs per game in either direction, often times you will see umpires who favor the home/away teams consistently. I have to admit Angel Hernandez did a great job at being unbiased in his bad calls, a lot of respect for that. 
# 
# Joe West I can't say the same for you, you were still mediocre at your best being in the 52nd percentile of umpires for Favor.


