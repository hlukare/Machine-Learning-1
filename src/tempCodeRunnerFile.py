import slate3k as slate
import re
import logging
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from operator import itemgetter


class DividePaths:

    def __init__(self, folder):
        self.path_list = list()
        pathlist = Path(folder).glob('*.pdf')
        for file in pathlist:
            self.path_list.append(file)


class JobDescription:

    def __init__(self, path):

        self.path = path
        self.summary = None
        self.experience = None
        self.corpus = list()
        self.parse()

    def parse(self):
        """
        extracts all the text of different regex and assigns the values to respective variables
        :return:
        """

        with open(self.path, 'r') as file:
            text = file.read()

        self.summary = TextPreprocessor().text_cleaning(text, 'Summary(.*)')
        self.experience = TextPreprocessor().text_cleaning(text, 'Experience(.*?)Education')
        self.corpus.append(self.summary)


class Resume:

    def __init__(self, path):

        self.path = path
        self.summary = None
        self.corpus = list()
        self.name = None
        self.experience = None
        self.value = None
        self.parse()

    def compare_with(self, obj):
        """
        it takes the jobDescription object as input and returns the score as output.
        :param obj:
        :return:
        """

        self.corpus.append(' '.join(obj.corpus))
        self.value = self.score(self.corpus, obj)
        return self.value

    def id(self):
        """
        appends id to the score of every individual's resume and returns a list of id and score.
        :return:
        """
        path = str(self.path).replace('.pdf', '')

        return [path, self.value]

    def modify(self, text):
        """
        Removes all the blank lines and returns a string.
        :param text:
        :return:
        """

        text = ' '.join(text)
        text = '\n'.join([line for line in text.splitlines() if line])

        return text

    def parse(self):
        """
        This method is used to parse through the PDF file. It also calls the text_cleaning method and then appends the
        cleaned_text to corpus.
        :return:
        """
        logging.propagate = False
        logging.getLogger().setLevel(logging.ERROR)

        with open(self.path, 'rb') as file:
            text = slate.PDF(file)
        text = self.modify(text)
        self.summary = TextPreprocessor().text_cleaning(text, '.*')
        self.corpus.append(self.summary)
        self.experience = TextPreprocessor().text_cleaning(text, 'Experience(.*?)Education')
        self.name = TextPreprocessor().text_cleaning(text, '(.*)Summary')

    def score(self, corpus, obj):
        """
        Takes list of texts as input and returns float value. The float value represents the similarity of the texts
        present in the corpus by creating bag_of_words.
        :param corpus:
        :param obj:
        :return:
        """

        cv = CountVectorizer(max_features=None)
        bag_of_words = cv.fit_transform(corpus).toarray()
        value = cosine_similarity(bag_of_words)
        value[0][1] = value[0][1] + self.experience / (obj.experience * 10)

        return value[0][1]


class SortId:

    def sort_scores(self, id_list=list(), my_list=list()):

        if len(my_list) == 0:
            id_list.sort(key=itemgetter(1), reverse=True)
            return id_list

        temp = list(zip(my_list, id_list))

        temp.sort(key=lambda x:x[1][1], reverse=True)

        return temp

    def find(self, id_list, my_list=list(), rank=0, score=0.0):

        length_list = len(id_list)

        if rank != 0:
            if rank > 0:

                return [id_list[l] for l in range(0, rank)]

            else:

                rank = length_list - abs(rank)

                return [id_list[l] for l in range(rank, length_list)]

        else:

            id_list = [l for l in id_list if l[1] >= score]

            return id_list


class TextPreprocessor:

    def text_cleaning(self, raw_text, regex):

        """
        Takes string as input. This method cleans the text by removing words called as stopwords
        and it returns a string.
       :param raw_text:
       :param regex:
       :return:
       """
        stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
                     'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
                     'itself',
                     'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that',
                     'these',
                     'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
                     'do',
                     'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                     'while',
                     'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during',
                     'before',
                     'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
                     'again',
                     'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
                     'each',
                     'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
                     'than',
                     'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']

        if regex == 'Experience(.*?)Education':
            raw_text = re.sub('[^a-zA-Z0-9]', ' ', raw_text)
            raw_text = re.findall(regex, raw_text)
            raw_text = ' '.join(raw_text)
            years = re.findall('([0-9]{1,2}).? years?', raw_text)
            months = re.findall('([0-9]{1,2}) months?', raw_text)

            return sum(list(map(int, years))) + (sum(list(map(int, months))) / 12)

        elif regex == '(.*)Summary':
            raw_text = re.split('\n', raw_text)
            return raw_text[0]

        raw_text = re.sub('[^a-zA-Z]', " ", raw_text).split()
        raw_text = ' '.join([word for word in raw_text if word not in stopwords])
        special_words = ['machine', 'learning', 'artificial', 'intelligence', 'deep', 'learning']
        abbrev = {'ml': 'machinelearning', 'ai': 'artificialintelligence', 'dl': 'deeplearning'}
        summary = re.findall(regex, raw_text)
        len_of_text = len(summary)

        for i in range(len_of_text):
            if summary[i].lower() in abbrev:
                summary[i] = abbrev[summary[i]]

        lis_length = len(special_words)

        for i in range(lis_length - 1):
            if special_words[i] + special_words[i + 1] in summary:
                summary.remove(special_words[i] + special_words[i + 1])
                summary.append(special_words[i])
                summary.append(special_words[i + 1])

        clean_text = ' '.join(summary).lower()

        return clean_text


if __name__ == '__main__':
    id_list = list()
    my_list = list()
    jobDescription = JobDescription("C:/Users/Harish/Desktop/Machine Learning/Resume_project/jobDescription1.txt")

    divide_obj = DividePaths("C:/Users/Harish/Desktop/Machine Learning/Resume_project/resume")
    for file in divide_obj.path_list:
        resume = Resume(file)
        print(resume.compare_with(jobDescription))
        id_list.append(resume.id())
    sort_id = SortId()
    print(sort_id.sort_scores(id_list))

    # Import necessary modules
# Import necessary modules
# Import necessary modules
import os

# Assuming 'data' contains the list of lists you provided
data = [['C:\\Users\\Harish\\Desktop\\Machine Learning\\Resume_project\\resume\\11981094', 0.7687122159121844], 
        ['C:\\Users\\Harish\\Desktop\\Machine Learning\\Resume_project\\resume\\64468610', 0.7324196639527136], 
        ['C:\\Users\\Harish\\Desktop\\Machine Learning\\Resume_project\\resume\\28078163', 0.7314350622203433], 
        # Other data here
       ]

# Specify the directory where you want to save the files
output_directory = "resume_similarity_results"

# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Iterate through the data and save each item to a separate file
for index, item in enumerate(data):
    file_path = os.path.join(output_directory, f"result_{index}.txt")
    with open(file_path, "w") as file:
        file.write(f"Resume Path: {item[0]}\nSimilarity Score: {item[1]}")






