# right click a node to crawl it.
# after it has been crawled, a few links will show up for it.
# if you want more nodes to show up for it, click it again.


# node data[0] is the current state of crawling. 0 - uncrawled, 1 - currently crawling, 2 - crawled
from __future__ import print_function

from threading import Thread

import pygame
import webbrowser

from grapy import *
from grapy.grapher import tupleSubtract
from crawlingfunctions import findlinksonpage


# if this is set to true, we will cycle through
# adds a new node to the graph near it's parent. assumes that it hasn't been crawled
def addnewnode(graph, name, parent):
    parentposition = graph.nodes[parent].position
    nodeposition = (parentposition[0] + 30, parentposition[1] + 30)
    n = Node(name, position=nodeposition)
    n.data = [0, 0, 0]
    n.data[0] = 0
    n.data[1] = []
    n.data[2] = 0

    graph.addNode(n)
    graph.addRelationship(name, parent)

# spawns a new node near a given parent node


def spawnfrommetadata(graph, parent):
    if not len(graph.nodes[parent].data[1]) > 0:
        return

    # killing some uncrawled nodes, because clearly they are not of interest

    # taking note of the new node name before removing it from the parent node's list
    newnodename = graph.nodes[parent].data[1][0]
    graph.nodes[parent].data[1] = graph.nodes[parent].data[1][1:]

    # checking to make sure the node doesn't already exist
    if newnodename in graph.nodes:
        spawnfrommetadata(graph, parent)
    else:
        addnewnode(graph, newnodename, parent)


# takes a graph to add the new node to. adds a true statement to the node's metadata along with a list of all of the pages crawled to the node's extra data, and the size of this list as the second element
# does the following:
# finds unique links on page
# the node should already exist, so update the node metadata to say it's been crawled
# create a few new nodes from it's metadata, and remove them from the metadata
def crawlthread(graph, page):
    print("CURRENTLY CRAWLING:", page)
    graph.nodes[page].data[0] = 1
    uniquelinks = findlinksonpage(page)

    print("DONE CRAWLING", page, "WAITING FOR LOCK AVAILABILITY.")
    graph.lock()
    graph.nodes[page].data[0] = 2
    graph.nodes[page].data[1] = uniquelinks
    graph.nodes[page].data[2] = len(uniquelinks)

    if len(uniquelinks) > graph.data[0]:
        graph.data[0] = len(uniquelinks)

    for i in range(0, 5):
        spawnfrommetadata(graph, page)

    graph.unlock()


# a custom draw function for the nodes.
def customdraw(screen, node, graph, position):
    # n produces a colour gradient between 0 and 254 depending on the number of relationships
    # n = (((1 + 1.0/(0.35*(relationships+1)))**(0.35*relationships)-1)/1.71828)*254 #tends to 254 as relaitonships tend to infinity

    # if the node has not been crawled, colour it grey.
    # if the node has been crawled, colour it more red depending on how many links it still has left to pop up, and totally blue when that is none.
    if node.data[0] == 2:  # if it has been crawled
        # ranges from 0 to 1. 1 being the most important
        importance = float(node.data[2]) / graph.data[0]
        node.radius = int(8 + 20 * importance)
        pygame.draw.circle(screen, (int(255 * importance), 0,
                                    255 - int(255 * importance)), position, node.radius, 0)

        f = pygame.font.Font(None, 20).render(node.UID, 1, (255, 255, 255))
        f2 = pygame.font.Font(None, 20).render(
            str(len(node.data[1])) + "/" + str(node.data[2]), 1, (255, 255, 255))
        # blitting the text with an x offset of 15 pixels
        screen.blit(f, tupleSubtract(position, (0, -10)))
        screen.blit(f2, tupleSubtract(position, (0, -23)))
    else:
        node.radius = 8
        pygame.draw.circle(screen, (100, 100, 100), position, node.radius, 0)

        textcolour = (255, 255, 255)

        if node.data[0] == 1:  # if is currently being crawled, make the text yellow
            textcolour = (255, 255, 0)

        f = pygame.font.Font(None, 20).render(node.UID, 1, textcolour)
        # blitting the text with an x offset of 15 pixels
        screen.blit(f, tupleSubtract(position, (0, -10)))


def openarticleinbrowser(article):
    webbrowser.open("http://en.wikipedia.org/wiki/" + article)

# assumes the graph is currently locked


def registernodeclick(graph, name):
    node = graph.nodes[name]
    if node.data[0]:  # if it has been crawled, pop another node from its metadata
        spawnfrommetadata(graph, name)
    else:
        t = Thread(target=crawlthread, args=(graph, name))
        t.start()


print("SETTING UP GRAPH AND GRAPHER...")
graph = Graph()
graph.data = [1]
g = Grapher(graph=graph)
g.setNodeDrawFunction(customdraw)
g.size = (1000, 800)
print("SETUP COMPLETE...")

tocrawl = input("\nWhich wikipedia page should we crawl?   ")

n = Node(tocrawl)
n.data = [0, 0, 0]
n.data[0] = False
n.data[1] = []
n.data[2] = 0

graph.addNode(n)

g.start()

while True:
    graph.lock()
    events = g.getEvents()
    for e in events:
        print(e)
        if e[0] == 1 and e[1] == 3 and e[2] is not None:
            registernodeclick(graph, e[2])
        elif e[0] == 1 and e[1] == 2 and e[2] is not None:
            openarticleinbrowser(e[2])

    graph.unlock()
