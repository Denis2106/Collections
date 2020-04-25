'''
GNU V2, Denis Kim 2020, deniskim2@me.com

Featured class for holding dict.

Features:
- access to dict values same as attributes (ex. dict['key'] == dict.key)
- default values
- selection prefixes for keys separately for each caller module
- load value with conversion from string according type of default value
- value change history
- available some standart dict methods:
    keys(), update(), get(), setdefault(), del ...

Updates
- update from dict to specific section
- method items()
- method section()
'''
import inspect

class Data:
    '''
        Methods:
        --------
        .use(<key>, <value>)
            set default value wich used for:
            - retrive value while other value not assigned
            - define type conversion for string parsing

        .clear(<key>)
            clear value. Will available default value

        .parse(<key>, <str>)
            parsing string with type conversion according with
            type of default value

        .update(<data>)
            updating items and values from other <class Data> or <class dict>

        .section(<section>)
            acces to item from section.
            return object of type Data

        .select(<prefix>, isGlobal=True)
            setting default prefix for caller module or all modules
            when prefix is defined for finding key using options:
                in first, key = <prefix> + <end> + <key>
                in second, key = <key>

            when isGlobal=False, selected prefix used only for call
            from current module. For each module used different prefix

            when isGloval=True, selected prefix used for all calls
            independent of caller module

            example:
                d = Data()
                d.a = 1; d.b=2; d.loc_a = 3
                d.select('loc')
                d.a
                    => 3
                d.b
                    => 2

        Attributes:
        -----------
        .history - dict with history of getting and setting for atribytes
                   {attribute: [[<module>.<function>, <new value>], ...]}

                   available only for atribytes in .history.keys()
                        start recording:    .history['key']=[]
                        stop recording:     del .history['key']
                        view history:       .history['key']
    '''
    def __init__(self, source=None, section=''):
        '''
        source - source object with data. Available type are dict, Data
        section - default selected section
        '''
        self.__dict__['prefix_end'] = '_'

        if source == None or type(source)==dict:
            if source == None:
                self.__dict__['_items'] = {}     # Values
            else:
                self.__dict__['_items'] = source

            self.__dict__['defaults'] = {}   # Default values
            self.__dict__['assigns'] = {}    # Признак что значение было присвоено явно
            self.__dict__['history'] = {}    # история изменения значения атрибута
            self.__dict__['sources'] = {}    # источники значений
            self.__dict__['prefixes'] = {}   # используемые префиксы для модулей
            self.__dict__['prefix'] = ''     # используемый глобальный префикс

        elif isinstance(source, Data):
            self.__dict__['_items'] = source._items
            self.__dict__['defaults'] = source.defaults
            self.__dict__['assigns'] = source.assigns
            self.__dict__['history'] = source.history
            self.__dict__['sources'] = source.sources
            self.__dict__['prefixes'] = source.prefixes
            self.__dict__['prefix'] = ''     # используемый глобальный префикс

            self.select(section, isGlobal=True)

#---------------------------------------------------------------
#   Public specific methods implementation
#   use(), clear(), parse(), section(), select()
#---------------------------------------------------------------

    # Определяет значение по умолчанию для атрибута
    def use(self, name, default, source=None):
        self.defaults[name] = default
        if not name in self._items: self._items[name] = None
        if not name in self.assigns: self.assigns[name] = None
        if not name in self.sources: self.sources[name] = source

    # Очищает один элемент
    def clear(self, name):
        self._items[name] = None
        self.assigns[name] = None
        self.add_history(name, caller='.clear')

    # Устанавливает значение атрибута из строки по типу соотв. defaults
    def parse(self, key, valueStr):
        varType = type(self.defaults[key])
        if varType == int: self._items[key] = int(valueStr)
        elif varType == float: self._items[key] = float(valueStr)
        elif varType == bool: self._items[key] = bool(valueStr)
        else: self._items[key] = valueStr

    # Access to items in section
    def section(self, section=None):
        if not section: section = ''
        return Data(self, section)

    # Устанавливает текущий префикс
    def select(self, prefix='', isGlobal=True):
        if prefix!='':
            newPrefix = prefix + self.prefix_end
        else:
            newPrefix = ''

        if isGlobal:
            # Меняем глобальный префикс
            self.__dict__['prefix'] = newPrefix
        else:
            module = self.get_caller_module()
            self.__dict__['prefixes'][module] = newPrefix

#---------------------------------------------------------------
#   Private methods implementation
#---------------------------------------------------------------
    # closest module from callstack with name != this module
    def get_caller_module(self):
        frames = inspect.getouterframes(inspect.currentframe())[1:]
        for f in frames:
            module = f.filename.split('/')[-1]
            if module != 'i_data.py':
                return module

    # return caller for function
    # idx = 1 caller for this function
    # idx = 2 caller for caller for this function
    def get_caller(self, idx=2):
        frames = inspect.getouterframes(inspect.currentframe())[1:]
        for f in frames:
            module = f.filename.split('/')[-1]
            if module != 'i_data.py':
                return module + '.' +f.function

    # current prefix is self.prefix or self.prefixes[caller module]
    def get_prefix(self):
        if len(self.__dict__['prefix']): return self.__dict__['prefix']

        module = self.get_caller_module()
        prefix = self.__dict__['prefixes'].get(module,'')
        return prefix

    # Возвращает префиксы для которых определен атрибут
    def find_prefix(self, key):
        prefixes = []
        if key in self._items: prefixes.append('')

        for k in self._items.keys():
            if k.endswith(self.prefix_end+key):
                prefixes.append(k[:-len(self.prefix_end+key)])

        return prefixes

    # Определяет полное имя ключа - с префиксом или без
    def make_key(self, key):
        if self.prefix != '':
            return self.prefix + key
        else:
            return key

#---------------------------------------------------------------
#   Standard dict methods implementation
#---------------------------------------------------------------
    def keys(self):
        if self.prefix=='':
            return self._items.keys()
        else:
            return [key[len(self.prefix):] for key in self._items.keys() if key.startswith(self.prefix)]

    def items(self):
        return [(k,self[k]) for k in self.keys()]

    def get(self, key, default=None):
        prefixKey = self.make_key(key)
        return self.__dict__['_items'].get(prefixKey, default)

    def setdefault(self, key, default):
        if key not in self.__dict__['_items'].keys():
            self._items[key] = default
        return self._items[key]

    # Дополняет словарь из другого экземпляра Data или dict
    def update(self, data, section=''):
        oldSection = self.prefix[:-1]
        self.select(section, isGlobal=True)
        try:

            if isinstance(data, Data):
                assert section=='', 'parameter section available only for update from dict'

                self._items.update(data._items)
                self.defaults.update(data.defaults)
                self.assigns.update(data.assigns)
                self.history.update(data.history)
                self.sources.update(data.sources)
            elif type(data) == dict:
                # Одновление из стандартного словаря
                for k,v in data.items():
                    key = self.make_key(k)
                    self.__dict__['_items'][key] = data[k]

                    # Добавляем в assigns все ключи из нового набора
                    # что бы их правильно обрабатывал getitem
                    if key not in self.assigns: self.assigns[key] = '.update'

                    # Обновляем историю по отслеживаемым элементам
                    if key in self.history: self.history[key].append(['.update', v])

        finally:
            self.select(oldSection, isGlobal=True)

        return self

    def __getattr__(self, reqName):
        '''Если атрибут обновлялся (.assigns[key])
           возвращаем его значение (._items[key])
           иначе возвращаем значение из .defaults[key]
        '''
        name = self.make_key(reqName)
        if not name: raise(IndexError('Bad index %s' % reqName))

        self.add_history(name)
        if name in self.__dict__['_items'].keys() and self.__dict__['_items'][name]:
            return self.__dict__['_items'][name]
        elif name in self.__dict__['defaults'].keys():
            return self.__dict__['defaults'][name]
        else:
            #print('_items:', self.__dict__['_items'].keys())
            #print('defaults:', self.__dict__['defaults'].keys())

            msg = 'Unknown key: %s' % reqName
            msg += ' at section: %s' % self.prefix[:-1] if self.prefix != '' else ''
            raise Exception(msg)


    def __getitem__(self, key):
        self.add_history(key)
        return self.__getattr__(key)


    def __setitem__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value
        else:
            key = self.make_key(key)
            self._items[key] = value
            if self.defaults.get(key)==None: self.defaults[key] = None
            self.add_history(key, value)


    def __setattr__(self, name, value):
        self.__setitem__(name, value)


    def __delitem__(self, key):
        if key in self._items: del self._items[key]
        if key in self.defaults: del self.defaults[key]
        if key in self.assigns: del self.assigns[key]


    def __delattr__(self, key):
        self.__delitem__(key)


    def __repr__(self):
        return str(self.items())


    def add_history(self, prefixKey, value=None, caller=None):
        #print("add_history prefixKey=", prefixKey)
        if prefixKey in self.history:
            if not caller: caller = self.get_caller(idx=3)
            if value!=None: self.assigns[prefixKey] = caller
            if type(self.history[prefixKey]) != list: self.__dict__['history'][prefixKey]=[]
            self.__dict__['history'][prefixKey].append( [caller, value] )
