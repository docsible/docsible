# Generated Documentation
## coffeemaker_morning
Description: Docsible coffemaker morning demo


| Field                | Value           |
|--------------------- |-----------------|
| Functional description | Role that make morning coffe |
| Requester            | Service one |
| Users                | ['service one', 'service two'] |
| Date dev             | 19/11/2023 |
| Date prod            | 19/11/2023 |
| Readme update            | 19/11/2023 |
| Version              | 0.0.1 |
| Time Saving              | 10 min |
| Category              | coffee |
| Sub category              | ['morning', 'coffee'] |


### Defaults
**These are static variables with lower priority**
#### File: main.yml
| Var          | Type         | Value       | Required    | Title       |
|--------------|--------------|-------------|-------------|-------------|
| temperature    | str   | 90  | True  | Temperature coffee |



### Vars

No vars available.


### Tasks
| Name | Module | Condition |
| ---- | ------ | --------- |
| Start brewing coffee | ansible.builtin.uri | False |
| Check coffee temperature | ansible.builtin.uri | False |
| Notify if coffee is ready | ansible.builtin.debug | True |
| Turn off coffee maker | ansible.builtin.uri | True |


## Task Flow Graphs

### Graph for main.yml
```mermaid
flowchart TD
  Start
  Start-->|Task| Start_brewing_coffee[start brewing coffee]
  Start_brewing_coffee-.->|End of Task| Start_brewing_coffee
  Start_brewing_coffee-->|Task| Check_coffee_temperature[check coffee temperature]
  Check_coffee_temperature-.->|End of Task| Check_coffee_temperature
  Check_coffee_temperature-->|Task| Notify_if_coffee_is_ready_when_coffee_temp_json_temperature____temperature[notify if coffee is ready]
  Notify_if_coffee_is_ready_when_coffee_temp_json_temperature____temperature---|When: coffee temp json temperature    temperature| Notify_if_coffee_is_ready_when_coffee_temp_json_temperature____temperature
  Notify_if_coffee_is_ready_when_coffee_temp_json_temperature____temperature-.->|End of Task| Notify_if_coffee_is_ready_when_coffee_temp_json_temperature____temperature
  Notify_if_coffee_is_ready_when_coffee_temp_json_temperature____temperature-->|Task| Turn_off_coffee_maker_when_coffee_temp_json_temperature____temperature[turn off coffee maker]
  Turn_off_coffee_maker_when_coffee_temp_json_temperature____temperature---|When: coffee temp json temperature    temperature| Turn_off_coffee_maker_when_coffee_temp_json_temperature____temperature
  Turn_off_coffee_maker_when_coffee_temp_json_temperature____temperature-.->|End of Task| Turn_off_coffee_maker_when_coffee_temp_json_temperature____temperature
```


## Playbook
```yml
---
- name: Demo morning coffee
  hosts: localhost
  connection: local
  roles:
    - coffeemaker_morning

```
## Playbook graph
```mermaid
flowchart TD
  localhost-->|Role| coffeemaker_morning[coffeemaker morning]
```

## Author Information
Lucian BLETAN

#### License
license (GPL-2.0-or-later, MIT, etc)

#### Minimum Ansible Version
2.1

#### Platforms
No platforms specified.