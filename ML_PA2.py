'''

PA-2: K-Means and GMM
Authors:
Amitabh Rajkumar Saini, amitabhr@usc.edu
Shilpa Jain, shilpaj@usc.edu
Sushumna Khandelwal, sushumna@usc.edu

Dependencies: 
1. numpy : pip install numpy
2. matplotlib : pip install matplotlib

Output:
Returns a k-means and gmm model, writes model parameters on console and generates the plot of the same

'''

import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math
import copy
import itertools


class k_means:
    '''
    k_means class defines functions and variables to run the k-means algorithm
    '''

    def __init__(self, input_data, n_clusters, max_limit, error_rate):
        '''
        Constructs k-means object
        :param input_data: input data to make the model
        :param n_clusters: no. of clusters to be generated
        :param max_limit: maximum number of iterations for convergence
        :param error_rate: error which can be accomodated in model
        :return: return object for running k-means
        '''
        self.input_data = input_data
        self.n_clusters = n_clusters
        self.error_rate = error_rate
        self.max_limit = max_limit
        self.error_rate = error_rate
        self.centroid = dict()  # {1:(),2:()..n_clusters}
        self.clusters = dict()  # {1:[(),(),(),],2:[(),(),(),]..n_clusters}

    def gen_random_centroid(self):
        '''
        Generates initial random centroids from the input data
        :return: returns nothing
        '''
        list_centroid = self.input_data[np.random.choice(self.input_data.shape[0], self.n_clusters, replace=False), :]
        for i in range(self.n_clusters):
            self.centroid[i] = list_centroid[i]
            self.clusters[i] = []

    def e_step(self):
        '''
        Runs e-step of the k-means, to find closest centroid and assign the data to that cluster
        :return: returns nothing
        '''
        for data in self.input_data:
            id_ = self.find_closest_centroid(data)
            self.clusters[id_].append(data)

    def find_closest_centroid(self, point):
        '''
        Finds the closest centroid to the input data point
        :param point: data point
        :return: returns closest cluster_id
        '''
        closest_dist = float("inf")
        closest_centroid = None

        for each in self.centroid.keys():
            dist = self.calculate_distance(self.centroid[each], point)
            if dist < closest_dist:
                closest_dist = dist
                centroid_id = each

        return centroid_id

    def calculate_distance(self, centroid, cluster):
        '''
        Calculates euclidean distance between 2 points
        :param centroid: point 1
        :param cluster: point 2
        :return: return euclidean distance
        '''
        return np.linalg.norm(centroid - cluster)

    def m_step(self):
        '''
        Runs m-step of k-means algorith to recompute centroids from clusters generated by e-step
        :return: returns nothing
        '''
        for key in self.clusters.keys():
            list_of_points = self.clusters[key]
            new_centroid = np.mean(list_of_points, axis=0)
            self.centroid[key] = new_centroid

    def execute(self):
        '''
        Runs the EM Algorith for gmm
        :return: returns nothing
        '''
        self.gen_random_centroid()
        current_error = float("inf")
        current_iteration = 1
        while current_error > self.error_rate and current_iteration < self.max_limit:
            self.e_step()
            old_centroid = copy.copy(self.centroid)  # copy dict
            self.m_step()
            new_centroid = copy.copy(self.centroid)  # copy dict
            dif_list = []
            for each in self.centroid:
                dif_list.append(abs(new_centroid[each] - old_centroid[each]))
            current_error = np.mean(dif_list)
            current_iteration += 1

    def get_metric(self):
        '''
        Calculates metric for a model
        :return: returns the metric value
        '''
        metric = 0
        for each in self.clusters:
            for point in self.clusters[each]:
                metric += self.calculate_distance(self.centroid[each], point)
        return metric

    def get_radii(self, cluster_id):
        '''
        Find maximum radii of a given cluster
        :param cluster_id: cluster_id
        :return: returns radius of the cluster
        '''
        radii = float('-inf')
        for point in self.clusters[cluster_id]:
            radii = max(radii, self.calculate_distance(self.centroid[cluster_id], point))
        return radii

    def plot(self):
        '''
        Plots the k-means cluster and write output to console
        :return: returns nothing
        '''
        colors = list("rgy")
        for each in self.clusters:
            temp = np.asarray(self.clusters[each])
            plt.scatter(temp[:, 0], temp[:, 1], color=colors.pop(), )
        print("------------K-Means------------")
        print("Centroid:")
        print(self.centroid)
        centers = np.asarray(list(self.centroid.values()))
        axes = plt.gca()
        plt.scatter(centers[:, 0], centers[:, 1], c='black')
        for i in range(self.n_clusters):
            axes.add_patch(plt.Circle(centers[i], self.get_radii(i), fc='#CCCCCC', lw=3, alpha=0.2, zorder=2))
        plt.title("K-Means")
        plt.show()


class gmm:
    '''
    gmm class defines functions and variables to run the gmm algorithm
    '''

    def __init__(self, data, max_iteration, n_clusters, threshold=0.5):
        '''
        Constructs gmm object
        :param data: input data to make the model
        :param max_iteration: maximum number of iterations for convergence
        :param n_clusters: no. of clusters to be generated
        :param threshold: error which can be accomodated in model
        :return: return object for running gmm
        '''
        self.input_data = data
        self.max_iteration = max_iteration
        self.n_clusters = n_clusters
        self.threshold = threshold
        self.ric = np.full((self.input_data.shape[0], n_clusters), 1 / self.n_clusters)
        for i in range(self.ric.shape[0]):
            x = random.uniform(0, 1)
            y = random.uniform(0, (1 - x))
            z = 1 - (x + y)
            self.ric[i] = np.asarray([x, y, z])
        # print(self.ric)
        self.mu = np.zeros((n_clusters, self.input_data.shape[1]))
        # print(self.mu)
        self.cov = np.zeros((n_clusters, self.input_data.shape[1], self.input_data.shape[1]))
        # print(self.cov)
        self.pi = np.zeros(n_clusters)
        self.likelihood = 0
        # print(self.pi)

    def probability_density(self, i, gaussian_id):
        '''
        Computes the probablility density function for multivariate normal distribution
        :param gaussian_id: gaussian_id
        :returns : return pdf(probability density function) value
        '''
        try:
            probability = 1 / pow((2 * math.pi), -self.n_clusters / 2) * pow(abs(np.linalg.det(self.cov[gaussian_id])),
                                                                             -1 / 2) * \
                          np.exp(-1 / 2 * np.dot(np.dot((self.input_data[i] - self.mu[gaussian_id]).T,
                                                        np.linalg.inv(self.cov[gaussian_id])),
                                                 (self.input_data[i] - self.mu[gaussian_id])))
        except:
            print(np.linalg.inv(self.cov[gaussian_id]))
        return probability

    def e_step(self):
        '''
        Runs e-step of the gmm, to calculate gaussian parameters mean,co-variance and amplitude
        :return: returns nothing
        '''
        for i in range(self.n_clusters):
            self.calculate_mu(i)
            self.calculate_pi(i)
            self.calculate_sigma(i)

    def m_step(self):
        '''
        Runs m-step of the gmm, to calculate responsibility/membership for each data point
        :return: returns nothing
        '''
        for i in range(self.n_clusters):
            self.calculate_ric(i)

    def calculate_mu(self, gaussian_id):
        """
        Computes the mean for a gaussian and updates the mean value
        :param gaussian_id: gaussian_id
        :returns : returns nothing
        """
        ric = self.ric[:, gaussian_id]
        avg = np.average(self.input_data, axis=0, weights=ric)
        self.mu[gaussian_id] = avg

    def calculate_sigma(self, gaussian_id):
        '''
        Computes the co-variance for a gaussian and updates the covariance matrix
        :param gaussian_id: gaussian_id
        :returns : returns nothing
        '''
        summ = np.zeros((self.input_data.shape[1], self.input_data.shape[1]))
        summ1 = np.zeros((self.input_data.shape[1], self.input_data.shape[1]))
        for i in range(self.input_data.shape[0]):
            data_temp = self.input_data[i].reshape(self.input_data.shape[1], 1)
            mu_temp = self.mu[gaussian_id].reshape(self.mu.shape[1], 1)
            diff_temp = data_temp - mu_temp
            summ += self.ric[i, gaussian_id] * np.dot(diff_temp, diff_temp.T)

        self.cov[gaussian_id] = summ / np.sum(self.ric[:, gaussian_id])

    def calculate_ric(self, gaussian_id):
        '''
        Computes the ric for all data points for a gaussian_id and updates the ric value
        :param gaussian_id: gaussian_id
        :returns : returns nothing
        '''
        for i in range(self.input_data.shape[0]):
            summ = 0
            for each in range(self.n_clusters):
                summ += self.pi[each] * self.probability_density(i, each)

            self.ric[i][gaussian_id] = self.pi[gaussian_id] * self.probability_density(i, gaussian_id) / summ
            # print(self.ric)

    def calculate_pi(self, gaussian_id):
        '''
        Computes the amplitude for a gaussian and updates the amplitude
        :param gaussian_id: gaussian_id
        :returns : returns nothing
        '''
        self.pi[gaussian_id] = np.sum(self.ric[:, gaussian_id]) / self.input_data.shape[0]

    def get_likelihood(self):
        '''
        Calculates the log likelihood
        :return : returns log likelihood
        '''
        new_likelihood = 0
        for i in range(self.input_data.shape[0]):
            temp = 0
            for k in range(self.n_clusters):
                temp += self.pi[k] * self.probability_density(i, k)
            new_likelihood += np.log(temp)

        return new_likelihood

    def execute(self):
        '''
        Runs the EM Algorith for gmm
        :return: returns nothing
        '''
        iterations = 0
        delta = float('inf')
        while delta > self.threshold and iterations < self.max_iteration:
            self.e_step()
            self.m_step()
            lld = self.get_likelihood()
            delta = lld - self.likelihood
            self.likelihood = lld
            iterations += 1

    def predict(self, X):
        '''
        Returns predicted labels using Bayes Rule to
        :param X: data points
        :return: predicted cluster based on highest responsibility gamma.
        '''
        labels = np.zeros(X.shape[0])

        for i in range(X.shape[0]):
            max_density = 0
            for c in range(self.n_clusters):
                density = self.pi[c] * self.probability_density(i, c)
                if max_density < density:
                    labels[i] = c
                    max_density = density

        return labels

    def plot(self):
        '''
        Plots the gmm and write output to console
        :return: returns nothing
        '''
        print("---------GMM----------")
        print("Means")
        print(self.mu)
        print("Amplitudes")
        print(self.pi)
        print("Covariance")
        print(self.cov)

        centers = np.zeros((self.n_clusters, 2))
        predicted_values = self.predict(self.input_data)
        axes = plt.gca()
        for c in range(self.n_clusters):
            max_density = 0
            point = None
            for i in range(self.input_data.shape[0]):
                density = math.log(self.probability_density(i, c))
                if max_density < density:
                    max_density = density
                    point = self.input_data[i]
            centers[c, :] = point
        print("Centers")
        print(centers)
        color_iter = itertools.cycle(['navy', 'cornflowerblue', 'gold', 'darkorange'])
        colors = list("rgy")
        plt.scatter(self.input_data[:, 0], self.input_data[:, 1], c=predicted_values, s=50, cmap='viridis', zorder=1)
        plt.scatter(centers[:, 0], centers[:, 1], c='black', s=300, alpha=0.5, zorder=2)

        for i, (mean, covar, color) in enumerate(zip(
                self.mu, self.cov, color_iter)):
            v, w = np.linalg.eigh(covar)
            v = 2. * np.sqrt(2.) * np.sqrt(v)
            u = w[0] / np.linalg.norm(w[0])
            angle = np.arctan(u[1] / u[0])
            angle = 180. * angle / np.pi
            ell = patches.Ellipse(mean, v[0], v[1], 180. + angle, color=color)
            ell.set_alpha(0.5)
            axes.add_artist(ell)
        plt.title("GMM")
        plt.show()


def main():
    '''
    Runner Program
    :return: returns nothing
    '''
    data = np.loadtxt('clusters.txt', delimiter=',')
    k_means_model = run_k_means(data, 10)
    k_means_model.plot()
    gmm_obj = gmm(data, 100, 3, 0.01)
    gmm_obj.execute()
    gmm_obj.plot()


def run_k_means(data, no_of_runs):
    '''
    Runs the k-means multiple times and gets the best model
    :param no of runs: #runs
    :return: returns best k-means model
    '''
    metrics = dict()
    for i in range(no_of_runs):
        k_obj = k_means(data, 3, 100, 0.01)
        k_obj.execute()
        metrics[k_obj] = k_obj.get_metric()
    key = min(metrics, key=metrics.get)
    print(metrics)
    return key


if __name__ == "__main__":
    main()