# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2014, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""
Utilities for running data through the TM, and analyzing the results.
"""



class TMTestMachine(object):
  """
  Base TM test machine class.
  """

  def __init__(self,
               tm):
    """
    @param tm (TM) Temporal memory
    """
    # Save member variables
    self.tm = tm


  def feedSequence(self, sequence, learn=True):
    """
    Feed a sequence through the TM.

    @param sequence (list) List of patterns, with None for resets
    @param learn    (bool) Learning enabled

    @return (list) List of sets containing predictive cells,
                   one for each element in `sequence`
    """
    results = []

    for pattern in sequence:
      if pattern == None:
        self.tm.reset()
      else:
        self.tm.compute(pattern, learn=learn)

      results.append(self.tm.predictiveCells)

    return results


  def computeDetailedResults(self, results, sequence):
    """
    Compute detailed results from results of `feedSequence`.

    @param results  (list) Results from `feedSequence`
    @param sequence (list) Sequence that generated the results

    @return (tuple) Contains:
                      `predictedActiveCellsList`     (list),
                      `predictedInactiveCellsList`   (list),
                      `predictedActiveColumnsList`   (list),
                      `predictedInactiveColumnsList` (list),
                      `unpredictedActiveColumnsList` (list)
    """
    predictedActiveCellsList = [set()]
    predictedInactiveCellsList = [set()]
    predictedActiveColumnsList = [set()]
    predictedInactiveColumnsList = [set()]
    unpredictedActiveColumnsList = [set()]

    for i in xrange(1, len(results)):
      pattern = sequence[i]

      predictedActiveCells = set()
      predictedInactiveCells = set()
      predictedActiveColumns = set()
      predictedInactiveColumns = set()
      unpredictedActiveColumns = set()

      if pattern != None:
        prevPredictedCells = results[i-1]

        for prevPredictedCell in prevPredictedCells:
          prevPredictedColumn = self.tm.connections.columnForCell(
                                  prevPredictedCell)

          if prevPredictedColumn in pattern:
            predictedActiveCells.add(prevPredictedCell)
            predictedActiveColumns.add(prevPredictedColumn)
          else:
            predictedInactiveCells.add(prevPredictedCell)
            predictedInactiveColumns.add(prevPredictedColumn)

        unpredictedActiveColumns = pattern - predictedActiveColumns

      predictedActiveCellsList.append(predictedActiveCells)
      predictedInactiveCellsList.append(predictedInactiveCells)
      predictedActiveColumnsList.append(predictedActiveColumns)
      predictedInactiveColumnsList.append(predictedInactiveColumns)
      unpredictedActiveColumnsList.append(unpredictedActiveColumns)

    return (predictedActiveCellsList,
            predictedInactiveCellsList,
            predictedActiveColumnsList,
            predictedInactiveColumnsList,
            unpredictedActiveColumnsList)


  @staticmethod
  def prettyPrintDetailedResults(detailedResults,
                                 sequence,
                                 patternMachine,
                                 verbosity=1):
    """
    Pretty print the detailed results from `feedSequence`.

    @param detailedResults (list)           Detailed results from
                                            `computeDetailedResults`
    @param sequence        (list)           Sequence that generated the results
    @param patternMachine  (PatternMachine) Pattern machine
    @param verbosity       (int)            Verbosity level

    @return (string) Pretty-printed text
    """
    from prettytable import PrettyTable
    table = PrettyTable(["Pattern",
                        "predicted active columns",
                        "predicted inactive columns",
                        "unpredicted active columns",
                        "# predicted active cells",
                        "# predicted inactive cells"])
    (
    predictedActiveCellsList,
    predictedInactiveCellsList,
    predictedActiveColumnsList,
    predictedInactiveColumnsList,
    unpredictedActiveColumnsList
    ) = detailedResults

    for i in xrange(len(sequence)):
      pattern = sequence[i]

      if pattern == None:
        table.add_row(["<reset>", 0, 0, 0, 0, 0])
        continue

      row = []

      row.append(patternMachine.prettyPrintPattern(pattern,
                                                   verbosity=verbosity))
      row.append(
        patternMachine.prettyPrintPattern(predictedActiveColumnsList[i],
                                          verbosity=verbosity))
      row.append(
        patternMachine.prettyPrintPattern(predictedInactiveColumnsList[i],
                                          verbosity=verbosity))
      row.append(
        patternMachine.prettyPrintPattern(unpredictedActiveColumnsList[i],
                                          verbosity=verbosity))
      row.append(len(predictedActiveCellsList[i]))
      row.append(len(predictedInactiveCellsList[i]))

      table.add_row(row)

    return table.get_string()
