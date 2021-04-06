import numpy as np
import random

class Decision:

    def __init__(self, engine):
        self._engine = engine
        self.params = {}
        self._rvs = {}

    ##############################################
    #              Public Methods                #  
    ##############################################

    def getName(self):
        return type(self).__name__

    def getInstanceName(self):
        className = type(self).__name__
        return className + '_' + str(self._getCount())

    def getLastInstanceName(self):
        className = type(self).__name__
        return className + '_' + str(self._getCount() - 1)

    def expand(self, nonterminal, params = {}):
        ret = self._engine._render(nonterminal, params)
        # ret, highlight_tree = self._engine.render(nonterminal, params)
        # has_map = False
        # if isinstance(ret, tuple):
            # ret, mapping = ret
            # has_map = True
        ret = ret.replace('{', '{{')
        ret = ret.replace('}', '}}')
        # if has_map:
        # return ret, dict(name=nonterminal, template=mapping)
        # return ret, highlight_tree
        return ret

    '''
    Choices 
    Choices are random variables. You can declare them,
    And the engine will chose their values for you. This is
    the only part of your program that can have randomness
    '''
    def addChoice(self, choice_name, values):
        """
         - choice_name: name of a RV
         - values: possible values of RV. Either a list, in which case it should be picked uniformly
            otherwise it is a dictionary with weights
        """
        if self._engine._isRenderingChoices:
            if choice_name in self._engine.choices:
                return
                
        self._rvs[choice_name] = values
        val = self._engine._pick_rv(choice_name, values)
        self._engine._addGlobalChoice(choice_name, val)


    def getChoice(self, key):
        return self._engine.choices[key]

    def hasChoice(self, key):
        return key in self._engine.choices



    '''
    State 
    State is global data that can be used to help future decisions
    know about previous decisions
    '''

    def getState(self, key):
        return self._engine.state[key]

    def hasState(self, key):
        return key in self._engine.state

    def setState(self, key, value):
        self._engine.state[key] = value


    '''
    Rubric 
    Rubrics are the labels you would need to calculate a grade
    (though they are not grades themselves). They should be a 
    function of the random variables
    '''
    # can only make a boolean true, never turns it false
    # we grade down. This should mean points off
    def turnOnRubric(self, key):
        self._engine.rubric[key] = True



    ##############################################
    #               To Overload                  #  
    ##############################################

    # Overload
    def updateRubric(self):
        pass

    # Overload
    def registerChoices(self):
        pass

    # Overload
    def render(self):
        """
        Renders the text after choices have been made, returning
        a template string with both text and format specifiers
        directing the enginine on what to render in that place.

        Usage notes:
            - Put nonterminals in format specifier for the engine to render.

            - Make sure to escape text curly braces with {{ and }}

            - To generate the same instance of a nonterminal in two places,
              use the same name inmultiple places.

            - To generate separate instance of a nonterminal in two places,
              append the nonterminal name with numbers _1, _2 etc.

        """
        className = type(self).__name__
        raise NotImplementedError('Method render needs to be implemented by ' + className)

    ##############################################
    #            Private Methods                 #  
    ##############################################

    # the engine can initialize current params
    def _setParams(self, params):
        self.params = params

    def _getRandomVariables(self):
        return self._rvs

    def _getCount(self):
        className = type(self).__name__
        key = className + '_count'
        if not self.hasState(key):
            self.setState(key, 0)
        return self.getState(key)

    def _incrementCount(self):
        className = type(self).__name__
        key = className + '_count'
        if not self.hasState(key):
            self.setState(key, 0)
        self.setState(className + '_count', self._getCount() + 1)
    

