import numpy as np
import matplotlib.pyplot as plt
import math
import re
import sys

# time library is imported but it is not to use for building algorithm and just for our report
import time


output_line_counter = 1
max_filter_length = 9
min_filter_length = 2
stopwords = open("English-Stop-Words.txt", "r", encoding="latin-1").read().splitlines()


def get_token_count(label, length_filter, stopword_filter):
    global max_filter_length, min_filter_length, stopwords
    tokens = dict()
    file_count = 0
    i = 1
    while True:
        # print("/train/train-{}-{:05d}.txt".format(label, i))
        try:
            with open(".\\train\\train-{}-{:05d}.txt".format(label, i), encoding="latin-1") as test_file:
                txt = test_file.read().lower()
                tokenized = list(filter(None, re.split('[^a-zA-Z]', txt)))

                if length_filter:
                    tokenized = [token for token in tokenized if min_filter_length < len(token) < max_filter_length]

                if stopword_filter:
                    tokenized = [token for token in tokenized if token not in stopwords]

                for token in tokenized:
                    if token in tokens:
                        tokens[token] += 1
                    else:
                        tokens[token] = 1
                file_count += 1
        except FileNotFoundError:
            #print('Build model for {} is done'.format(label))
            break
        i += 1
    return tokens, file_count


def build_model(model_filename, length_filter=False, stopword_filter=False):
    ham_token, ham_file_count = get_token_count('ham', length_filter, stopword_filter)
    spam_token, spam_file_count = get_token_count('spam', length_filter, stopword_filter)

    words = set(list(ham_token.keys()) + list(spam_token.keys()))

    for word in words:
        if word not in ham_token.keys():
            ham_token[word] = 0
        if word not in spam_token.keys():
            spam_token[word] = 0

    ham_token_smooth = {key: ham_token[key] + 0.5 for key in words}
    spam_token_smooth = {key: spam_token[key] + 0.5 for key in words}
    total_ham = sum(list(ham_token_smooth.values()))
    total_spam = sum(list(spam_token_smooth.values()))

    ham_model = {key: ham_token_smooth[key]/total_ham for key in words}
    spam_model = {key: spam_token_smooth[key]/total_spam for key in words}

    linecount = 1
    # now sort token by alphabetic order
    sorted_keys = sorted(words)
    model_file = open(model_filename, "w+")
    for key in sorted_keys:
        model_file.write('{}  {}  {}  {}  {}  {}\n'.format(
            linecount, key, ham_token[key], ham_model[key], spam_token[key], spam_model[key]))
        linecount += 1
    return ham_file_count, spam_file_count


def classify_set(prior_ham, prior_spam, fileset, nb):
    i = 1
    spam_count = 0
    ham_count = 0
    classifications = list()
    while True:
        try:
            classification = ""
            score_ham = 0
            score_spam = 0
            with open(".\\test\\test-{}-{:05d}.txt".format(fileset, i), encoding="latin-1") as test_file:
                txt = test_file.read().lower()
                tokenized = re.split('[^a-zA-Z]', txt)
                for token in tokenized:
                    if token in nb:
                        ham_token_score, spam_token_score = nb[token]
                        score_ham = score_ham + math.log10(float(ham_token_score))
                        score_spam = score_spam + math.log10(float(spam_token_score))
                    else:
                        pass
                # add prior
                score_ham = score_ham + math.log10(prior_ham)
                score_spam = score_spam + math.log10(prior_spam)
                if score_spam >= score_ham:
                    spam_count += 1
                    classification = "spam"
                else:
                    ham_count += 1
                    classification = "ham"
                classifications.append((classification, score_spam, score_ham))
        except FileNotFoundError:
            #print('Classification test for %s done.' % fileset)
            break
        i += 1
    return classifications, spam_count, ham_count


def load_model(model_filename):
    model_file = open(model_filename)
    lines = model_file.readlines()
    model = dict()
    for line in lines:
        words = line.split("  ")
        model[words[1]] = (words[3], words[5])
    return model


def output_results(classifications, output_file, class_under_test):
    global output_line_counter
    for classification_index, (classification, score_spam, score_ham) in enumerate(classifications):
        judgement = "wrong"
        if classification == class_under_test:
            judgement = "right"
        output_file.write("{}  test-{}-{:05d}.txt  {}  {}  {}  {}  {}\n".format(output_line_counter, class_under_test, classification_index + 1, classification, score_ham, score_spam, class_under_test, judgement))
        output_line_counter += 1


def NB_Classifer(ham_file_count, spam_file_count, model_filename, output_filename):
    nb = load_model(model_filename)
    output_file = open(output_filename, "w+")
    global output_line_counter
    output_line_counter = 1

    # compute priors
    prior_ham = ham_file_count/(ham_file_count+spam_file_count)
    prior_spam = spam_file_count/(ham_file_count+spam_file_count)

    hamtest_classifications, hamtest_wrong_count, hamtest_right_count = classify_set(prior_ham, prior_spam, "ham", nb)
    output_results(hamtest_classifications, output_file, "ham")
    print("test set file count: ham right: "+str(hamtest_right_count)+" ham wrong:"+str(hamtest_wrong_count)+" total ham: "+str(hamtest_right_count + hamtest_wrong_count))

    spamtest_classifications, spamtest_right_count, spamtest_wrong_count = classify_set(prior_ham, prior_spam, "spam", nb)
    output_results(spamtest_classifications, output_file, "spam")
    print("test set file count: spam right: "+str(spamtest_right_count)+" spam wrong:"+str(spamtest_wrong_count)+" total spam: "+str(spamtest_right_count + spamtest_wrong_count))

    print("total accuracy: (" + str(spamtest_right_count)+" + "+str(hamtest_right_count)+")/("+str(hamtest_right_count + hamtest_wrong_count)+" + "+str(spamtest_right_count + spamtest_wrong_count)+")= "+str((spamtest_right_count+hamtest_right_count)/(hamtest_right_count + hamtest_wrong_count+spamtest_right_count + spamtest_wrong_count)))
    b = 1

    print("\n\nHAM Statistics")
    #accuracy_ham = hamtest_right_count / (hamtest_right_count + hamtest_wrong_count)
    #print('accuracy(ham): ' + str(hamtest_right_count) + "/(" + str(hamtest_right_count) + "+" + str(hamtest_wrong_count) + ") = " + str(accuracy_ham))
    precision_ham = hamtest_right_count / (hamtest_right_count + spamtest_wrong_count)
    print("precision(ham): " + str(hamtest_right_count) + "/(" + str(hamtest_right_count) + "+" + str(spamtest_wrong_count) + ")= " + str(precision_ham))
    recall_ham = hamtest_right_count / (hamtest_right_count + hamtest_wrong_count)
    print("recall(ham): " + str(hamtest_right_count) + "/(" + str(hamtest_right_count) + "+" + str(hamtest_wrong_count) + ")= " + str(recall_ham))
    f_measure_ham = (b * b + 1) * precision_ham * recall_ham / (b * b * precision_ham + recall_ham)
    print("f_measure_ham: " + str(f_measure_ham))

    print("\n\nSPAM Statistics")
    #accuracy_spam = spamtest_right_count / (spamtest_right_count + spamtest_wrong_count)
    #print('accuracy(ham): ' + str(spamtest_right_count) + "/(" + str(spamtest_right_count) + "+" + str(spamtest_wrong_count) + ") = " + str(accuracy_spam))
    precision_spam = spamtest_right_count / (spamtest_right_count + hamtest_wrong_count)
    print("precision(spam): " + str(spamtest_right_count) + "/(" + str(spamtest_right_count) + "+" + str(hamtest_wrong_count) + ") = " + str(precision_spam))
    recall_spam = spamtest_right_count / (spamtest_right_count + spamtest_wrong_count)
    print("recall(spam): " + str(spamtest_right_count) + "/(" + str(spamtest_right_count) + "+" + str(spamtest_wrong_count) + ") = " + str(recall_spam))
    f_measure_spam = (b * b + 1) * precision_spam * recall_spam / (b * b * precision_spam + recall_spam)
    print("f_measure_spam: " + str(f_measure_spam))

    confusion_matrix = np.array([[hamtest_right_count, hamtest_wrong_count], [spamtest_wrong_count, spamtest_right_count]])
    fig, ax = plt.subplots()
    im = ax.imshow(confusion_matrix, cmap="Reds")
    ax.set_xticks(np.arange(2))
    ax.set_yticks(np.arange(2))
    ax.set_xticklabels(["HAM", "SPAM"])
    ax.set_yticklabels(["HAM", "SPAM"])
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    for j in range(0, 2):
        for i in range(0, 2):
            plt.text(j, i, '{}'.format(confusion_matrix[i, j]), ha='center', va='center',
                     bbox=dict(boxstyle='round', facecolor='white', edgecolor='0.3'))
    plt.title("Confusion Matrix for {}".format(model_filename))
    plt.xlabel("Classified As")
    plt.ylabel("Real Class")
    print(confusion_matrix)


def __main__():
    baseline_name, baseline_result = "baseline-model.txt", "baseline-result.txt"
    stopword_name, stopword_result = "stopword-model.txt", "stopword-result.txt"
    wordlength_name, wordlength_result = "wordlength-model.txt", "wordlength-result.txt"

    custom_model = input("Do you want to use custom model? If no, original trainning / test set will be run  (Y/N)")
    if custom_model.lower() == 'y':
        baseline_name = input("Please enter baseline experiment model name: ")
        baseline_result = input("Please enter baseline experiment result name: ")
        stopword_name = input("Please enter stop-word experiment model name: ")
        stopword_result = input("Please enter stop-word  experiment result name: ")
        wordlength_name = input("Please enter word-length experiment model name: ")
        wordlength_result = input("Please enter word-length experiment result name: ")

    num_runs = 1
    baseline_total_time = 0
    baseline_build_time = 0
    baseline_class_time = 0

    stopword_total_time = 0
    stopword_build_time = 0
    stopword_class_time = 0

    wordlength_total_time = 0
    wordlength_build_time = 0
    wordlength_class_time = 0

    hybrid_total_time = 0
    hybrid_build_time = 0
    hybrid_class_time = 0

    for i in range(0, num_runs):

        print("\nStarting iteration #%d" % i)

        print("\nStarting baseline tests")
        start_time = time.time()*1000
        ham_file_count, spam_file_count = build_model(baseline_name)
        build_end = time.time() * 1000
        # file in training set
        print("training set: ham: "+str(ham_file_count) +" spam: "+ str(spam_file_count))
        # print("Model build computation time: %fms" % (build_end-start_time))
        baseline_build_time = baseline_build_time + (build_end-start_time)

        NB_Classifer(ham_file_count, spam_file_count, baseline_name, baseline_result)
        end_time = time.time()*1000
        # print("Classification computation time: %fms" % (end_time-build_end))
        baseline_class_time = baseline_class_time + (end_time-build_end)

        #print("Total computation time: %fms\n" % (end_time-start_time))
        baseline_total_time = baseline_total_time + (end_time-start_time)



        print("\nStarting stopword tests")
        start_time = time.time()*1000
        ham_file_count, spam_file_count = build_model(stopword_name, stopword_filter=True)
        build_end = time.time() * 1000
        #print("Model build computation time: %fms" % (build_end-start_time))
        stopword_build_time = stopword_build_time + (build_end-start_time)

        NB_Classifer(ham_file_count, spam_file_count, stopword_name, stopword_result)
        end_time = time.time()*1000
        #print("Classification computation time: %fms" % (end_time-build_end))
        stopword_class_time = stopword_class_time + (end_time-build_end)

        #print("Total computation time: %fms\n" % (end_time-start_time))
        stopword_total_time = stopword_total_time + (end_time-start_time)


        print("\nStarting wordlength tests")
        start_time = time.time()*1000
        ham_file_count, spam_file_count = build_model(wordlength_name, length_filter=True)
        build_end = time.time() * 1000
        #print("Model build computation time: %fms" % (build_end-start_time))
        wordlength_build_time = wordlength_build_time + (build_end-start_time)

        NB_Classifer(ham_file_count, spam_file_count, wordlength_name, wordlength_result)
        end_time = time.time()*1000
        #print("Classification computation time: %fms" % (end_time-build_end))
        wordlength_class_time = wordlength_class_time + (end_time-build_end)

        #print("Total computation time: %fms\n" % (end_time-start_time))
        wordlength_total_time = wordlength_total_time + (end_time-start_time)


        print("\nStarting hybrid tests")
        start_time = time.time()*1000
        ham_file_count, spam_file_count = build_model("hybrid-model.txt", stopword_filter=True, length_filter=True)
        build_end = time.time() * 1000
        #print("Model build computation time: %fms" % (build_end-start_time))
        hybrid_build_time = hybrid_build_time + (build_end-start_time)

        NB_Classifer(ham_file_count, spam_file_count, "hybrid-model.txt", "hybrid-result.txt")
        end_time = time.time()*1000
        #print("Classification computation time: %fms" % (end_time-build_end))
        hybrid_class_time = hybrid_class_time + (end_time-build_end)

        #print("Total computation time: %fms\n" % (end_time-start_time))
        hybrid_total_time = hybrid_total_time + (end_time-start_time)

    print("\nBaseline:")
    print("Total time: %f" % (baseline_total_time/num_runs))
    print("Buld time: %f" % (baseline_build_time/num_runs))
    print("Classification time: %f" % (baseline_class_time/num_runs))

    print("\nStopwords:")
    print("Total time: %f" % (stopword_total_time/num_runs))
    print("Buld time: %f" % (stopword_build_time/num_runs))
    print("Classification time: %f" % (stopword_class_time/num_runs))

    print("\nWordlength:")
    print("Total time: %f" % (wordlength_total_time/num_runs))
    print("Buld time: %f" % (wordlength_build_time/num_runs))
    print("Classification time: %f" % (wordlength_class_time/num_runs))

    print("\nHybrid:")
    print("Total time: %f" % (hybrid_total_time/num_runs))
    print("Buld time: %f" % (hybrid_build_time/num_runs))
    print("Classification time: %f" % (hybrid_class_time/num_runs))

    total_times = (baseline_total_time/num_runs, stopword_total_time/num_runs, wordlength_total_time/num_runs, hybrid_total_time/num_runs)
    build_times = (baseline_build_time/num_runs, stopword_build_time/num_runs, wordlength_build_time/num_runs, hybrid_build_time/num_runs)
    class_times = (baseline_class_time/num_runs, stopword_class_time/num_runs, wordlength_class_time/num_runs, hybrid_class_time/num_runs)

    num_models = 4
    ind = np.arange(num_models)

    fig, ax = plt.subplots()
    total_bars = ax.bar(ind, total_times, 0.25)
    build_bars = ax.bar(ind + 0.25, build_times, 0.25)
    class_bars = ax.bar(ind + 0.5, class_times, 0.25)

    ax.set_title("Computation Times")
    ax.set_xticks(ind + 0.25 / 2)
    # ax.set_xticklabels(("Baseline", "Stopword", "Wordlength"))
    ax.set_xticklabels(("Baseline", "Stopword", "Wordlength", "Hybrid"))
    ax.legend((total_bars[0], build_bars[0], class_bars[0]), ("Total", "Build", "Classification"))

    # num_models = 4
    # ind = np.arange(num_models)
    # fig, ax = plt.subplots()
    # ax.set_xticks(np.arange(4))
    # ax.set_title("Comparing Results")

    # ax.set_xticklabels(["Baseline", "Stop-word", "Word-length", "Hybrid"])
    # plt.plot([0.9125*100,0.91375*100,0.92*100,0.91625*100])
    # plt.plot([0.91841*100,0.91949*100,0.92471*100,0.92090*100])
    # plt.plot([0.90566*100,0.90713*100,0.91467*100,0.91102*100])
    # plt.ylabel("Accurancy (in %)")
    # plt.legend(('Total Accurancy(Precision)', 'Ham (F-1 Measurement)', 'Spam (F-1 Measurement)'), loc='lower right')
    # plt.legend(('Ham (F-1 Measurement)', 'Spam (F-1 Measurement)'), loc='lower right')

    plt.show()


if __name__ == "__main__":
    __main__()
