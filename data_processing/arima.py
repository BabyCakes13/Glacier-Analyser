#!/usr/bin/env python3

import pandas as pd
from pandas.plotting import register_matplotlib_converters
from statsmodels.tsa.arima_model import ARIMA

# fixed the no background matplotlib bug
# matplotlib.use('gtk3cairo')

# fixing the future pandas warning
register_matplotlib_converters()


class Arima:
    def __init__(self, dataset):
        self.dataset = dataset

    def start(self, count):
        predictions = []
        output = None
        train, test, history = self.make_test_train(self.dataset)

        # TODO: this might be removed and just specify period to ARIMA directly
        fake_dates = pd.date_range(history[0][0], periods=100, freq='M')
        future_dates = pd.date_range(self.dataset[len(self.dataset) - 1][0], periods=count + 1, freq='M')

        for index in range(len(test) + count):
            print("estimating on: ", history)
            real_dates, ndsi = zip(*history)
            try:
                model = ARIMA(ndsi, order=(5, 2, 0), dates=fake_dates)
                model_fit = model.fit()
                output = model_fit.forecast(steps=count)
            except Exception:
                # prepare next iteration of model estimating
                if index < len(test):
                    observed = test[index][1]
                    history.append((test[index][0], observed))
                    continue

            predicted = output[0][0]
            error = output[1][0]

            print("OUTPUT: ", output)
            print("PREDICTED: ", predicted)
            print("ERROR: ", error)

            if index < len(test):
                observed = test[index][1]
                # prepare next iteration of model estimating
                history.append((test[index][0], observed))
                predictions.append((test[index][0], predicted))
                print('predicted=%f, expected=%f' % (predicted, observed))
            else:
                for predicted in output[0]:
                    # prepare next iteration of model estimating
                    history.append((future_dates[index - len(test)].date(), predicted))
                    predictions.append((future_dates[index - len(test)].date(), predicted))
                    index += 1
                break

        return predictions

    @staticmethod
    def make_test_train(dataset):
        """
        Split the input data set into training, testing and history
        """
        test_size = int(len(dataset) * 0.66)
        train, test = dataset[0:test_size], dataset[test_size:len(dataset)]
        history = [x for x in train]

        return train, test, history
