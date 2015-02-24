__author__ = 'arthur'

import csv
from operator import itemgetter
import operator

class record(object):
    def __init__(self, line):
        self.id = int(line[0])
        self.id2 = dict()
        self.label = int(line[10])
        self.rcrd = line[1:11]
        self.record_dict = dict()
        self.record_dict["CT"] = int(self.rcrd[0])
        self.record_dict["UCSZ"] = int(self.rcrd[1])
        self.record_dict["UCSH"] = int(self.rcrd[2])
        self.record_dict["MA"] = int(self.rcrd[3])
        self.record_dict["SEC"] = int(self.rcrd[4])
        self.record_dict["BN"] = int(self.rcrd[5])
        self.record_dict["BC"] = int(self.rcrd[6])
        self.record_dict["NN"] = int(self.rcrd[7])
        self.record_dict["M"] = int(self.rcrd[8])
        self.record_dict["OK"] = int(self.rcrd[9])
        self.id2[self.id] = self.record_dict

    def __str__(self):
        return "id: " + str(self.id) + ", ct: " + str(self.record_dict["CT"]) + ", ucsz: " + str(self.record_dict["UCSZ"]) + ", ucsh: " + str(self.record_dict["UCSH"]) + ", ma: " + str(self.record_dict["MA"]) + ", sec: " + str(self.record_dict["SEC"]) + ", bn: " + str(self.record_dict["BN"]) + ", bc: " + str(self.record_dict["BC"]) + ", nn: " + str(self.record_dict["NN"]) + ", m: " + str(self.record_dict["M"]) + ", ok: " + str(self.label)

class tree_node(object):
    def __init__(self):
        self.nodeType = "Node"
        self.level = 0
        self.splitAttribute = 99
        self.splitThreshold = 0
        self.left_child_complete = False
        self.right_child_complete = False
        self.left_child_node = None
        self.right_child_node = None
        self.parent_node = None
        self.is_leaf = True
        self.data = dict()

    def calculate_targets_frequencies(self):
        calculate_split = dict()
        for identity in self.data.keys():
            if self.data[identity]["OK"] in calculate_split.keys():
                calculate_split[self.data[identity]["OK"]] += 1
            else:
                calculate_split[self.data[identity]["OK"]] = 0
        return calculate_split



class decision_tree(object):
    def __init__(self):
        self.tree = tree_node()
        self.trainingData = None

    def create(self, filename):
        current_node = self.tree
        self.readCSV(current_node, filename)

    def readCSV(self, node, filename):
        with open(filename) as f:
            flag = False
            reader = csv.reader(f)
            for row in reader:
                if flag is False:
                    flag = True
                else:
                    rw = record(row)
                    node.data[rw.id] = rw.record_dict

    def resetTree(self):
        return 1


    def trainTree(self):
        current_node = self.tree
        notDone = True
        while notDone:
            self.split_node(current_node)
            if current_node.left_child_node.is_leaf:
                current_node.left_child_node.nodeType = "Leaf"
                current_node.left_child_complete = True
            if current_node.right_child_node.is_leaf:
                current_node.right_child_node.nodeType = "Leaf"
                current_node.right_child_complete = True
            if current_node.left_child_complete and current_node.right_child_complete:
                while current_node.left_child_complete and current_node.right_child_complete and current_node.level > 0:
                    current_node = current_node.parent_node
                if current_node.left_child_complete and current_node.right_child_complete and current_node.level == 0:
                    notDone = False
                    continue
            if not current_node.left_child_complete:
                current_node.left_child_complete = True
                current_node = current_node.left_child_node
                continue
            if current_node.left_child_complete and not current_node.right_child_complete:
                current_node.right_child_complete = True
                current_node = current_node.right_child_node
                continue

    def getin(self, tlist):
        count = 0
        elt = -100
        indices = []
        for t in tlist:
            if (elt < t[1]):
                indices.append(count)
                elt = t[1]
            count += 1
        return indices

    def find_best_attribute(self, gini_dict):
        sanity_check = gini_dict.keys()
        if len(sanity_check) == 1:
            tuple_list = sorted(gini_dict[sanity_check[0]], key= lambda x: x[1])
            if (tuple_list != []):
                return tuple_list[0]
            else:
                return []


    def split_node(self, node):
        attributes = ["CT", "UCSZ", "UCSH", "MA", "SEC", "BN", "BC", "NN", "M"]
        temp_dict = dict()
        ginis = dict()
        bestGini = dict()
        for attr in attributes:
            ginis[attr] = dict()
            for record_id in node.data.keys():
                temp_dict[record_id] = node.data[record_id][attr]

            tuple_list = sorted(temp_dict.items(), key=itemgetter(1))

            index_list = self.getin(tuple_list)
            # print index_list

            split_calculations = []
            for index in index_list:
                pared_down_list = tuple_list[0:index]
                calculate_split = dict()

                for tuples in pared_down_list:
                    identity = tuples[0]
                    if node.data[identity]["OK"] in calculate_split.keys():
                        calculate_split[node.data[identity]["OK"]] += 1
                    else:
                        calculate_split[node.data[identity]["OK"]] = 0
                # if (0 in calculate_split.keys()) == False:
                #     calculate_split[0] = 0
                # elif (1 in calculate_split.keys() == False):
                #     calculate_split[1] = 0
                split_calculations.append((index, calculate_split))

            ginis_x = dict()
            ginis_x[attr] = []
            for pairs in split_calculations:
                index = pairs[0]
                counts = pairs[1]
                if counts != {}:
                    # print attr + " " + str(counts)
                    # print counts
                    if 0 not in counts.keys():
                        left = 0
                    else:
                        left = counts[0]

                    if 1 not in counts.keys():
                        right = 0
                    else:
                        right = counts[1]

                    if left+right != 0:
                        gini_this = 1 - (float(left)/(left+right))**2 - (float(right)/(left+right))**2
                    else:
                        gini_this = 1
                    ginis_x[attr].append((index, gini_this))

            min_tuple = (attr, 100)
            for x in ginis_x[attr]:
                if min_tuple[1] > x[1]:
                    min_tuple = (attr, x)
                else:
                    continue

            # print ginis_x
            #
            #
            # min_attr = dict()
            # min_attrs = list()
            # min_tuple = (attr,100)
            # print "hi - " + str(ginis[attr].keys())
            # for x in [min(ginis[attr].keys())]:
            #     if min_tuple[1] > ginis[attr][x]:
            #         min_tuple = (attr, ginis[attr][x])
            #     else:
            #        continue

            # print index_list
            if (len(self.find_best_attribute(ginis_x)) == 0):
                return

            to_find = self.find_best_attribute(ginis_x)[0]
            gini = self.find_best_attribute(ginis_x)[1]
            for num in range(0, len(index_list)):
                if to_find == index_list[num]:
                    bestGini[attr] = (num, gini)
                    # print gini

        splitting_attribute = ""
        minGini = 1.1
        for attr in attributes:
            if bestGini[attr][1] < minGini:
                minGini = bestGini[attr][1]
                splitting_attribute = attr
            else:
                continue

        # print minGini
        if splitting_attribute in bestGini.keys():
            print "HEY GUYS!"
            splitting_value = bestGini[splitting_attribute][0]
            node.left_child_node = tree_node()
            node.right_child_node = tree_node()

            node.left_child_node.parent_node = node
            node.left_child_node.level = node.left_child_node.parent_node.level + 1
            node.right_child_node.parent_node = node
            node.right_child_node.level = node.right_child_node.parent_node.level + 1

            self.fill_children(node, attributes, splitting_attribute, splitting_value)

    def fill_children(self, current_node, attributes, splitting_attribute, splitting_value):
        print "attributes remaining " + str(attributes)

        if len(attributes) == 0:
            return

        if splitting_attribute == "":
            return


        for record_id in current_node.data.keys():
            if current_node.data[record_id][splitting_attribute] <= splitting_value:
                current_node.left_child_node.data[record_id] = current_node.data[record_id]
            else:
                current_node.right_child_node.data[record_id] = current_node.data[record_id]

        print "STARTING WITH " + splitting_attribute + " " + str(splitting_value)
        print "----------------------------------------------------------------------"

        print "Left node data STARTING"
        #for x in current_node.left_child_node.data.keys():
        #    print str(x) + " " + str(current_node.left_child_node.data[x])
        print "split is: " + str(current_node.left_child_node.calculate_targets_frequencies())
        # current_node.left_child_node.is_leaf()
        print "Left node data ENDING"
        print "----------------------------------------------------------------------"
        print ""
        print ""
        print ""
        print "----------------------------------------------------------------------"
        print "Right node data STARTING"
        #for x in current_node.right_child_node.data.keys():
        #    print str(x) + " " + str(current_node.right_child_node.data[x])
        print "split is: " + str(current_node.right_child_node.calculate_targets_frequencies())
        # current_node.right_child_node.is_leaf()
        print "Right node data ENDING"
        print "----------------------------------------------------------------------"

        print "DONE WITH " + splitting_attribute + " " + str(splitting_value)
        #attributes.remove(splitting_attribute)
        # self.split_node(current_node.right_child_node, attributes)
        # self.split_node(current_node.left_child_node, attributes)



def main():
    tr = decision_tree()
    tr.create("training.csv")
    tr.trainTree()


main()