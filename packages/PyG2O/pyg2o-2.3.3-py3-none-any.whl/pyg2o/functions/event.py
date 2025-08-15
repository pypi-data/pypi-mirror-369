
from functools import wraps

eventList           = {}
disabledEventList   = []

async def callEvent(evtName : str, **kwargs : list):
    """
    This function will notify (call) every handler bound to specified event.
    Original: [callEvent](https://gothicmultiplayerteam.gitlab.io/docs/0.3.0/script-reference/shared-functions/event/callEvent/)
    
    ## Declaration
    ```python
    def callEvent(evtName : str, **kwargs : list)
    ```
    
    ## Parameters
    * `str` **name**: the name of the event
    * `**dict` **kwargs**: the variable number of arguments.
    
    ## Usage
    ```python
    import g2o
    
    g2o.addEvent('testEvt')
    
    @g2o.event('testEvt')
    def onTestEvent(**kwargs):
        print(f'{kwargs['name']} called my beautiful test event')
        
    g2o.callEvent('testEvt', name = 'Diego')
    ```
    """
    
    if evtName in eventList and evtName not in disabledEventList:
        for event in eventList[evtName]:
            
            event['function'].eventName = evtName
            result = await event['function'](**kwargs)
        
def addEvent(name : str):
    """
    This function will register a new event with specified name.
    Events can be used to notify function(s) when something will happen, like player joins the server, etc.
    Original: [addEvent](https://gothicmultiplayerteam.gitlab.io/docs/0.3.0/script-reference/shared-functions/event/addEvent/)
    
    ## Declaration
    ```python
    def addEvent(name)
    ```
    
    ## Parameters
    * `str` **name**: the name of the event
    
    ## Usage
    ```python
    import g2o
    
    g2o.addEvent('testEvt')
    ```
    """
    if name not in eventList:
        eventList[name] = []
    
def event(event_name: str, priority: int = 9999) -> None:
    def inlineEvt(func):
        if event_name not in eventList:
            addEvent(event_name)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        eventList[event_name].append({'function': wrapper, 'priority': priority})
        eventList[event_name].sort(key = lambda x: x['priority'])
        return wrapper
    return inlineEvt
    
def removeEventHandler(name : str, func : object):
    """
    This function will unbind function from specified event.
    Original: [removeEventHandler](https://gothicmultiplayerteam.gitlab.io/docs/0.3.0/script-reference/shared-functions/event/removeEventHandler/)
    
    ## Declaration
    ```python
    def removeEventHandler(name : str, func : object)
    ```
    
    ## Parameters
    * `str` **name**: the name of the event
    * `object` **func**: the reference to a function which is currently bound to specified event.
    
    ## Usage
    ```python
    import g2o
    
    @g2o.event('onTime')
    def onTimeEvt(**kwargs):
        print('Calling only once')
        g2o.removeEventHandler('onTime', onTimeEvt)
    ```
    """
    if not name in eventList:
        pass
    
    for index, item in enumerate(eventList[name]):
        if item['function'] == func:
            del eventList[name][index]
            
def toggleEvent(name : str, toggle : bool):
    '''
    !!! note
        By default every event is toggled `on` (enabled).
        
    This function will toggle event (enable or disable it globally). By toggling event off, you can completely disable certain event from calling it's handlers.
    Original: [toggleEvent](https://gothicmultiplayerteam.gitlab.io/docs/0.3.0/script-reference/shared-functions/event/toggleEvent/)
    
    ## Declaration
    ```python
    def toggleEvent(name : str, toggle : bool)
    ```
    
    ## Parameters
    * `str` **name**: the name of the event
    * `bool` **toggle**: `false` if you want to disable the event, otherwise true.
    
    ## Usage
    ```python
    import g2o
    
    @g2o.event('onTime')
    def onTimeEvt(**kwargs):
        print('Calling only once')
        g2o.toggleEvent('onTime', false)
    ```
    '''
    if not toggle and name not in disabledEventList:
        disabledEventList.append(name)
    elif toggle and name in disabledEventList:
        disabledEventList.remove(name)
        
def removeEvent(name : str):
    '''
    !!! warning
        Removing an event also cause all event handlers to unregister.
    This function will unregister an event with specified name.
    Original: [removeEvent](https://gothicmultiplayerteam.gitlab.io/docs/0.3.0/script-reference/shared-functions/event/removeEvent/)
    
    ## Declaration
    ```python
    def removeEvent(name : str)
    ```
    
    ## Parameters
    * `str` **name**: the name of the event
    
    ## Usage
    ```python
    import g2o
    
    @g2o.event('onTime')
    def onTimeEvt(**kwargs):
        print('Calling only once')
        g2o.removeEvent('onTime')
    ```
    '''
    if name in eventList:
        eventList.pop(name)

## registering default events

addEvent('onInit')
addEvent('onExit')
addEvent('onTick')
addEvent('onTime')
addEvent('onBan')
addEvent('onUnban')

addEvent('onPlayerChangeColor')
addEvent('onPlayerChangeFocus')
addEvent('onPlayerChangeHealth')
addEvent('onPlayerChangeMana')
addEvent('onPlayerChangeMaxHealth')
addEvent('onPlayerChangeMaxMana')
addEvent('onPlayerChangeWeaponMode')
addEvent('onPlayerChangeWorld')

addEvent('onPlayerCommand')
addEvent('onPlayerDamage')
addEvent('onPlayerDead')
addEvent('onPlayerDisconnect')
addEvent('onPlayerDropItem')
addEvent('onPlayerEnterWorld')
addEvent('onPlayerJoin')
addEvent('onPlayerMessage')
addEvent('onPlayerMobInteract')
addEvent('onPlayerRespawn')
addEvent('onPlayerShoot')
addEvent('onPlayerSpellCast')
addEvent('onPlayerSpellSetup')
addEvent('onPlayerTakeItem')
addEvent('onPlayerTeleport')
addEvent('onPlayerToggleFaceAni')
    
addEvent('onPlayerEquipAmulet')
addEvent('onPlayerEquipArmor')
addEvent('onPlayerEquipBelt')
addEvent('onPlayerEquipHandItem')
addEvent('onPlayerEquipHelmet')
addEvent('onPlayerEquipMeleeWeapon')
addEvent('onPlayerEquipRangedWeapon')
addEvent('onPlayerEquipRing')
addEvent('onPlayerEquipShield')
addEvent('onPlayerEquipSpell')

addEvent('onPlayerSpawnForPlayer')
addEvent('onPlayerUnspawnForPlayer')

addEvent('onPacket')

addEvent('onPlayerUseCheat')

addEvent('onNpcActionFinished')
addEvent('onNpcActionSent')
addEvent('onNpcChangeHostPlayer')
addEvent('onNpcCreated')
addEvent('onNpcDestroyed')

addEvent('onWebsocketConnect')
addEvent('onWebsocketDisconnect')