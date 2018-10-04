# CatBot
IRC bot using DynamoDB backend

### Config
#### DynamoDB Table
Schema:
* Partition Key: `entity`
* Sort Key: `item`
* Value Key(s):
  * `value`

#### Boto3 Config
Default location: Bot's working directory
Default name: `boto.json`
Content: (See `boto_example.json`)

**Note:** keys not required if provided by the environment (such as EC2 instance role)

#### Bot Config
By default, stored under the `entity` name "**config**" in the DynamoDB table from the `boto.json` file. The ini file's section headers are used for the `item` name. The `value` is a dictionary/hash of the values for that section.

### Development

#### First Time Setup
```
pyvenv env
. env/bin/activate
pip3 install -e .
```

#### Morning Routine
```
. env/bin/activate
```

#### Running the Bot
```
catbot
```
