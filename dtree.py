__author__ = "arthur"

import pandas as pd

def indices_next(tlist):
    count = 0
    elt = -100
    indices = []
    for t in tlist:
        if (elt < t[1]):
            indices.append(count)
            elt = t[1]
        count += 1
    return indices

def summed_list(ls):
    for elt in range(0, len(ls)):
        if elt != 0:
            ls[elt] += ls[elt-1]
    return ls

class TreeNode(object):
    def __init__(self):
        self.data = pd.DataFrame()
        self.node_type = "Node"
        self.node_gini = 0.0
        self.parent = None
        self.left_child_node = None
        self.left_child_complete = False

        self.right_child_node = None
        self.right_child_complete = False
        self.level = 0

    def compute_gini_new_node(self):
        split_dict = self.data["OK"].value_counts().to_dict()
        if (len(split_dict) == 2):
            print "Size of split_dict is 2"
            zero_count = float(split_dict[0])
            one_count = float(split_dict[1])
            gini = 1 - (zero_count/(zero_count+one_count))**2 - (one_count/(zero_count+one_count))**2
            self.node_gini = gini

    def is_leaf(self):
        list_of_label_splits = self.data["OK"].value_counts().tolist()
        if len(list_of_label_splits) < 2:
            return True
        elif list_of_label_splits[0] == 0 or list_of_label_splits[1] == 0:
            return True
        else:
            return False


class DecisionTree(object):
    def __init__(self):
        self.root = TreeNode()
        self.used_attributes = set()

    def create(self, filename):
        current_node = self.root
        current_node.data = pd.read_csv(filename)
        self.train()

    def test(self, filename):
        current_node = self.root
        csv = pd.read_csv(filename)
        # print csv




    def train(self):
        current_node = self.root
        self.split(current_node)

    def split(self, current_node):
        all_indices = []
        attributes_start = current_node.data.columns[1:10]

        # iterate over a starting list of attribute strings, which lets us look at the structure of each col of interest
        attribute_ginis = dict()
        hold_ginis = []
        for attribute in attributes_start:
            if attribute not in self.used_attributes:
                attribute_ginis[attribute] = []
                # hold_ginis will hold the gini coefficients of every possible splitting condition to find the best one
                # attribute_df uses built in pandas functions to sort by attribute, THEN by ID
                attribute_df = current_node.data.sort([attribute,"ID"])
                # attribute_vals are the actual sorted values of the individual attribute
                attribute_vals = attribute_df[attribute]
                # buckets is a histogram of the different attribute value counts.
                buckets = attribute_vals.value_counts()
                # since attribute_vals is sorted, we can use this to know the offset
                series = buckets.sort_index()
                summedlist = summed_list(series.tolist())
                count = 0
                for element in summedlist:
                    # we get the sorted list of attribute values, and using elt, the summed indices, we grab the
                    # data that's been sectioned up (see attribute_vals, buckets, etc)
                    subsection = attribute_df[:element]
                    # this is a seriess
                    val_counts = subsection["OK"].value_counts()
                    series_size = val_counts.size
                    if series_size == 2:
                        # then we know this node will split and it is not a leaf node
                        left = val_counts[0]
                        right = val_counts[1]
                        if (left != 0 or right != 0):
                            gini = 1 - (float(left)/(left+right))**2 - (float(right)/(left+right))**2
                            tpl = (gini, count, element, attribute)
                            attribute_ginis[attribute].append(tpl)
                            #hold_ginis.append(tpl)
                    count += 1

            #print attribute_ginis
        slimmer_ginis = []
        for attribute in attributes_start:
            if attribute not in self.used_attributes:
                tuple_list = sorted(attribute_ginis[attribute], key= lambda x: x[0])
                if len(tuple_list) > 0:
                    slimmer_ginis.append(tuple_list[0])
        first_tuple_is_best = sorted(slimmer_ginis, key= lambda x: x[0])
        if (len(first_tuple_is_best) > 0):
            start_tuple = first_tuple_is_best[0]
        else:
            return
        current_node.node_gini = start_tuple[0]
        attribute_df = current_node.data.sort([start_tuple[3],"ID"])
        current_node.left_child_node = TreeNode()
        current_node.right_child_node = TreeNode()
        current_node.left_child_node.data = attribute_df[:start_tuple[2]]
        current_node.right_child_node.data = attribute_df[start_tuple[2]:]
        print start_tuple[3]
        print "left is " + str(current_node.left_child_node.data["OK"].value_counts().to_dict())
        print "right is " + str(current_node.right_child_node.data["OK"].value_counts().to_dict())

        current_node.left_child_node.compute_gini_new_node()
        current_node.right_child_node.compute_gini_new_node()
        left_gini = current_node.left_child_node.node_gini
        right_gini = current_node.right_child_node.node_gini
        print "left gini is " + str(left_gini)
        print "right gini is " + str(right_gini)
        if max(left_gini, right_gini) == right_gini:
            current_node = current_node.right_child_node
        else:
            current_node = current_node.left_child_node
        self.used_attributes.add(start_tuple[3])

        self.split(current_node)

def main(filename):
    dt = DecisionTree()
    dt.create(filename)
   # dt.test("test.csv")

main("training_train.csv")