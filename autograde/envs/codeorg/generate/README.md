We use this folder to store scripts that help us generate student programs.

We use IdeaToText package to conduct rubric sampling.

Generated files will be JavaScript files, stored under `../server/program/`

# Idea2Text Tutorial

The official tutorial is here: http://web.stanford.edu/class/cs398/handouts/ideaToText.html

A few notes:

1. Each coding block should have its own file (with many decisions that coding block needs to make)
2. `getChoice('name', {})`, the `name` chosen should not contain any `_`. Use camel case instead.
3. `render()` function, we can actually return a string with brackets on nodes we want to evaluate. 
For example, if we have a node `DecideNumber`, then we can return `"Alice chose {DecideNumber}"`, 
and the node will be automatically expanded.
4. Using string brackets in render will not help pass context parameters. Instead, use `self.expand('DecideNumber', params={'context':1})`
5. Context can be retrieved anywhere in the Decision class by `self.params['context']`. 
This greatly helps re-use Decision class to generate different nodes.

**Make decision and keep decision:**

Idea2Text is flexible enough to let you retrieve a previous random decision and its determined value
and use in later evaluation.

This is crucial for code generation, particularly related to variable names.

```python
class ScoreVarName(Decision):
    def registerChoices(self):
        values = {}
        for _ in range(20):
            name = ''.join(random.choices(string.ascii_lowercase, k=5))
            values[name] = 2

        values['scores'] = 200
        values['score'] = 20
        values['Scores'] = 20
        values['Scs'] = 20
        values['Scres'] = 20

        self.addChoice('score_var_name', values)

    def render(self):
        return self.getChoice("score_var_name")
```

This class will decide which name we take for a random variable. Once we decided, we need to be able 
to use this for future expansions. For example:

```python
class DecScore(Decision):
    def registerChoices(self):
        values = {}
        for num in range(0, 100):
            values[num] = 1

        self.addChoice('apple_click_dec_num', values)

    def updateRubric(self):
        self.turnOnRubric('AppleClickEvent score decreased, not increased')

    def render(self):
        num = self.getChoice('apple_click_dec_num')
        code = '\t {} -= {}; \n'.format(self.expand('ScoreVarName'), num)
        return code
```

We call `self.expand('ScoreVarName')` to retrieve the correct variable name. We cannot, however, 
call `self.getChoice('score_var_name')`, as this gives us an error. 

**Using context:**

```python
class FixedNumber(Decision):
    def registerChoices(self):
        values = {}
        for num in range(50, 280):
            values[str(num)] = 1
        self.addChoice('NewFixedPos{}'.format(self.params['pos']), values)

    def render(self):
        return self.getChoice('NewFixedPos{}'.format(self.params['pos']))
```

This class, when passed with different context, can generate different values.

