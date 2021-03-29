import csv
import operator
import pandas as pd

release_years = ["2014", "2015", "2016"]
number_of_genres = 6
movies_per_genre = 30

# -----------------------------------------------------

tsv_file = open("title.basics.tsv")
read_tsv = csv.reader(tsv_file, delimiter="\t")

movies = []
for row in read_tsv:
    if row[5] in release_years and row[1] == 'movie':
        movies.append([row[0], row[5], row[8]])

tsv_file.close()

print("Read in movies from release years - ", len(movies))
# -----------------------------------------------------

min_ttval = 10000000
max_ttval = 0
for row in movies:
    val = float(row[0][2:])
    if val < min_ttval:
        min_ttval = val
    if val > max_ttval:
        max_ttval = val

print("Found max-min")
# -----------------------------------------------------

csv_file = open("title.ratings.tsv")
csv_reader = csv.reader(csv_file, delimiter="\t")

filtered_ratings = []
first = True
for row in csv_reader:
    if first:
        first = False
        continue
    val = float(row[0][2:])
    if val <= max_ttval and val >= min_ttval and float(row[2]) > 100:
        filtered_ratings.append(row)

csv_file.close()

print("Read in ratings - ", len(filtered_ratings))
# -----------------------------------------------------

movies = [[str(i) for i in x] for x in movies]
filtered_ratings = [[str(i) for i in x] for x in filtered_ratings]

movies = pd.DataFrame(movies)
filtered_ratings = pd.DataFrame(filtered_ratings)

movie_ratings = movies.merge(filtered_ratings, how='inner', on=0)

movie_ratings = movie_ratings.values.tolist()

print("Joined sets")
# -----------------------------------------------------

for row in movie_ratings:
    row[4] = int(row[4])

movie_ratings = sorted(movie_ratings, key=operator.itemgetter(4), reverse=True)

print("Sorted by number of reviews")
# -----------------------------------------------------

genres_dict = {}

for row in movie_ratings:
    genres = row[2].split(",")
    for genre in genres:
        if genre in genres_dict:
            genres_dict[genre] += 1
        else:
            genres_dict[genre] = 1

genres_list = sorted(genres_dict.items(), key=operator.itemgetter(1), reverse=True)

print("Got genres list")
# -----------------------------------------------------

individual_sets = []

for i in range(number_of_genres):
    our_set = []
    for row in movie_ratings:
        if genres_list[i][0] in row[2].split(","):
            our_set.append(row)
        if len(our_set) >= movies_per_genre:
            break
    individual_sets.append(our_set)

for i in range(number_of_genres):
    with open('data/individual/' + genres_list[i][0] + '_movies_list.csv', mode='w') as data_file:
        data = csv.writer(data_file, delimiter=',')
        data.writerow(['title', 'year', 'genres', 'avg_rating', 'num_votes'])
        for row in individual_sets[i]:
            data.writerow(row)

print("Wrote individual list")
# -----------------------------------------------------

to_scrape = []
for my_set in individual_sets:
    for row in my_set:
        if row not in to_scrape:
            to_scrape.append(row)

with open('data/joined_list.csv', mode='w') as data_file:
    data = csv.writer(data_file, delimiter=',')
    data.writerow(['title', 'year', 'genres', 'avg_rating', 'num_votes'])
    for row in to_scrape:
        data.writerow(row)

print("Wrote joined list - ", len(to_scrape))
# -----------------------------------------------------

with open('data/genres_list.csv', mode='w') as data_file:
    data = csv.writer(data_file, delimiter=',')
    data.writerow(['genre', 'num_movies'])
    for row in genres_list:
        data.writerow(row)

print("Wrote genres to csv")
# -----------------------------------------------------

with open('data/all_reviews.csv', mode='w') as data_file:
    data = csv.writer(data_file, delimiter=',')
    data.writerow(['title', 'year', 'genres', 'avg_rating', 'num_votes'])
    for row in movie_ratings:
        data.writerow(row)

print("Wrote reviews to csv")
# -----------------------------------------------------
