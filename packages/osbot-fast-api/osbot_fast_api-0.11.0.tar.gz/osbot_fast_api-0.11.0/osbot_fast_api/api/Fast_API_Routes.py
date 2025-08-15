import functools
import inspect
from typing                                                       import get_type_hints
from fastapi                                                      import APIRouter, FastAPI, HTTPException
from osbot_utils.type_safe.Type_Safe                              import Type_Safe
from osbot_utils.decorators.lists.index_by                        import index_by
from osbot_utils.type_safe.Type_Safe__Primitive                   import Type_Safe__Primitive
from fastapi.exceptions                                           import RequestValidationError
from osbot_utils.type_safe.type_safe_core.shared.Type_Safe__Cache import type_safe_cache
from osbot_fast_api.utils.type_safe.Type_Safe__To__BaseModel      import type_safe__to__basemodel


class Fast_API_Routes(Type_Safe):       # refactor to Fast_API__Routes
    router : APIRouter
    app    : FastAPI = None
    prefix : str
    tag    : str

    def __init__(self, **kwargs):
        from osbot_utils.utils.Str import str_safe
        from osbot_utils.utils.Misc import lower

        super().__init__(**kwargs)
        self.prefix = f'/{lower(str_safe(self.tag))}'

    def add_route(self,function, methods):
        path = self.parse_function_name(function.__name__)
        self.router.add_api_route(path=path, endpoint=function, methods=methods)
        return self

    def add_route_with_body(self, function, methods):
        sig        = inspect.signature(function)                                                                # Get function signature
        type_hints = get_type_hints(function)                                                                   # Get type annotations

        type_safe_conversions = {}                                                                              # Map param_name -> (Type_Safe class, BaseModel class)
        primitive_field_types = {}                                                                              # Track which fields are Type_Safe__Primitive

        for param_name, param in sig.parameters.items():                                                        # Process each parameter
            if param_name == 'self':                                                                            # Skip self parameter
                continue
            param_type = type_hints.get(param_name)                                                             # Get parameter's type hint
            if param_type and inspect.isclass(param_type):                                                      # Check if it's a class type
                if issubclass(param_type, Type_Safe) and not issubclass(param_type, Type_Safe__Primitive):      # Type_Safe but not primitive

                    annotations = type_safe_cache.get_class_annotations(param_type)                             # For Type_Safe classes, also track their primitive fields
                    for field_name, field_type in annotations:                                                  # Check each field in the Type_Safe class
                        if isinstance(field_type, type) and issubclass(field_type, Type_Safe__Primitive):       # If field is Type_Safe__Primitive
                            if param_name not in primitive_field_types:                                         # Initialize dict if needed
                                primitive_field_types[param_name] = {}
                            primitive_field_types[param_name][field_name] = field_type                          # Store primitive field info

                    basemodel_class = type_safe__to__basemodel.convert_class(param_type)                        # Convert Type_Safe to BaseModel
                    type_safe_conversions[param_name] = (param_type, basemodel_class)                           # Store conversion mapping

        if type_safe_conversions:                                                                               # Need wrapper if Type_Safe params exist
            @functools.wraps(function)
            def wrapper(**kwargs):                                                                              # Wrapper to handle conversions
                converted_kwargs = {}                                                                           # Store converted parameters
                for param_name, param_value in kwargs.items():                                                  # Process each parameter value
                    if param_name in type_safe_conversions:                                                     # Handle Type_Safe parameters
                        type_safe_class, _ = type_safe_conversions[param_name]                                  # Get the Type_Safe class
                        if isinstance(param_value, dict):                                                       # If value came as dict (from JSON)
                            # Convert primitive fields back to Type_Safe__Primitive instances
                            if param_name in primitive_field_types:                                             # Check if has primitive fields
                                for field_name, primitive_class in primitive_field_types[param_name].items():   # For each primitive field
                                    if field_name in param_value:                                               # If field is present
                                        param_value[field_name] = primitive_class(param_value[field_name])      # Convert to Type_Safe__Primitive
                            converted_kwargs[param_name] = type_safe_class(**param_value)                       # Create Type_Safe instance
                        else:                                                                                   # If value is BaseModel instance
                            data = param_value.model_dump()                                                     # Convert to dict
                            # Convert primitive fields here too
                            if param_name in primitive_field_types:                                             # Check if has primitive fields
                                for field_name, primitive_class in primitive_field_types[param_name].items():   # For each primitive field
                                    if field_name in data:                                                      # If field is present
                                        data[field_name] = primitive_class(data[field_name])                    # Convert to Type_Safe__Primitive
                            converted_kwargs[param_name] = type_safe_class(**data)                              # Create Type_Safe instance
                    else:
                        converted_kwargs[param_name] = param_value                                              # Pass through unchanged

                try:
                    result = function(**converted_kwargs)                                                       # Call original function
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"{type(e).__name__}: {e}")                     # Convert exceptions to HTTP 400

                if isinstance(result, Type_Safe):                                                               # Convert Type_Safe return to dict
                    return type_safe__to__basemodel.convert_instance(result).model_dump()                       # Type_Safe -> BaseModel -> dict
                return result                                                                                   # Return unchanged

            # Build new parameters with BaseModel types
            new_params = []                                                                                     # Build new parameter list for wrapper
            for param_name, param in sig.parameters.items():                                                    # Process each original parameter
                if param_name == 'self':                                                                        # Skip self
                    continue
                if param_name in type_safe_conversions:                                                         # Replace Type_Safe with BaseModel
                    _, basemodel_class = type_safe_conversions[param_name]                                      # Get the BaseModel class
                    new_params.append(inspect.Parameter(                                                        # Create new parameter with BaseModel type
                        name=param_name,
                        kind=param.kind,
                        default=param.default,
                        annotation=basemodel_class
                    ))
                else:
                    new_params.append(param)                                                                    # Keep parameter unchanged

            # Set the new signature on the wrapper
            wrapper.__signature__ = inspect.Signature(parameters=new_params)                                    # Set new signature on wrapper

            # Also update annotations for FastAPI
            wrapper.__annotations__ = {}                                                                        # Build new annotations dict
            for param_name, param_type in type_hints.items():                                                   # Process each type hint
                if param_name in type_safe_conversions:                                                         # Use BaseModel for Type_Safe params
                    _, basemodel_class = type_safe_conversions[param_name]
                    wrapper.__annotations__[param_name] = basemodel_class
                else:
                    wrapper.__annotations__[param_name] = param_type                                            # Keep original annotation

            return_type = type_hints.get('return', None)                                                        # Get return type annotation
            if return_type and inspect.isclass(return_type):                                                    # Check if return type is a class
                if issubclass(return_type, Type_Safe) and not issubclass(return_type, Type_Safe__Primitive):    # Type_Safe but not primitive
                    basemodel_return = type_safe__to__basemodel.convert_class(return_type)                      # Convert to BaseModel for FastAPI
                    wrapper.__annotations__['return'] = basemodel_return                                        # Update return type annotation

            path = self.parse_function_name(function.__name__)                                                  # Parse function name to route path
            self.router.add_api_route(path=path, endpoint=wrapper, methods=methods)                             # Register route with FastAPI
            return self
        else:
            return self.add_route(function=function, methods=methods)                                           # No conversion needed, add directly

    def add_route_delete(self, function):
        return self.add_route(function=function, methods=['DELETE'])

    def add_route_get(self, function):
        import functools
        sig                     = inspect.signature(function)                                               # Get function signature
        type_hints              = get_type_hints(function)                                                  # Get type annotations
        primitive_conversions   = {}                                                                        # Map param_name -> (Type_Safe__Primitive class, primitive base type)
        type_safe_conversions   = {}                                                                        # Map param_name -> (Type_Safe class, BaseModel class)
        needs_return_conversion = False                                                                     # Flag if return type needs Type_Safe -> BaseModel conversion
        basemodel_return        = None                                                                      # BaseModel class for return type

        for param_name, param in sig.parameters.items():                                                    # Process each parameter
            if param_name == 'self':                                                                        # Skip self parameter
                continue
            param_type = type_hints.get(param_name)                                                         # Get parameter's type hint
            if param_type and inspect.isclass(param_type):                                                  # Check if it's a class type
                if issubclass(param_type, Type_Safe__Primitive):                                            # Handle Type_Safe__Primitive parameters
                    primitive_base = param_type.__primitive_base__                                          # Get the primitive base (str, int, float)
                    if primitive_base is None:                                                              # If not explicitly set, search MRO
                        for base in param_type.__mro__:                                                     # Walk up the class hierarchy
                            if base in (str, int, float):                                                   # Find the primitive type
                                primitive_base = base
                                break
                    if primitive_base:                                                                      # Store conversion info
                        primitive_conversions[param_name] = (param_type, primitive_base)
                elif issubclass(param_type, Type_Safe):                                                     # Handle regular Type_Safe parameters
                    basemodel_class = type_safe__to__basemodel.convert_class(param_type)                    # Convert Type_Safe class to BaseModel
                    type_safe_conversions[param_name] = (param_type, basemodel_class)                       # Store conversion info

        return_type = type_hints.get('return', None)                                                        # Get return type annotation
        if return_type and inspect.isclass(return_type):                                                    # Check if return type is a class
            if issubclass(return_type, Type_Safe) and not issubclass(return_type, Type_Safe__Primitive):    # Type_Safe but not primitive
                needs_return_conversion = True                                                              # Mark for conversion
                basemodel_return = type_safe__to__basemodel.convert_class(return_type)                      # Create BaseModel for FastAPI

        if primitive_conversions or type_safe_conversions or needs_return_conversion:                       # Need wrapper if any conversions required
            @functools.wraps(function)
            def wrapper(*args, **kwargs):                                                                   # Wrapper to handle conversions
                converted_kwargs = {}                                                                       # Store converted parameters
                validation_errors = []                                                                      # Collect validation errors

                for param_name, param_value in kwargs.items():                                              # Process each parameter value
                    if param_name in primitive_conversions:                                                 # Handle Type_Safe__Primitive params
                        type_safe_primitive_class, _ = primitive_conversions[param_name]                    # Get the Type_Safe__Primitive class
                        try:
                            converted_kwargs[param_name] = type_safe_primitive_class(param_value)           # Convert to Type_Safe__Primitive instance
                        except (ValueError, TypeError) as e:                                                # Catch conversion errors
                            validation_errors.append({                                                      # Format as FastAPI validation error
                                'type': 'value_error',
                                'loc': ('query', param_name),
                                'msg': str(e),
                                'input': param_value
                            })
                    elif param_name in type_safe_conversions:                                               # Handle Type_Safe params (complex objects in GET)
                        type_safe_class, _ = type_safe_conversions[param_name]                              # Get the Type_Safe class
                        converted_kwargs[param_name] = param_value                                          # Placeholder - needs custom query param parsing
                    else:
                        converted_kwargs[param_name] = param_value                                          # Pass through unchanged

                if validation_errors:                                                                       # Raise validation errors if any
                    raise RequestValidationError(validation_errors)

                if args:                                                                                    # Call with positional args if present
                    result = function(*args, **converted_kwargs)
                else:                                                                                       # Call with keyword args only
                    result = function(**converted_kwargs)

                if needs_return_conversion and isinstance(result, Type_Safe):                               # Convert Type_Safe return to dict
                    return type_safe__to__basemodel.convert_instance(result).model_dump()                   # Type_Safe -> BaseModel -> dict
                elif isinstance(result, Type_Safe__Primitive):                                              # Convert primitive return to base type
                    return result.__primitive_base__(result)                                                # Extract primitive value
                return result                                                                               # Return unchanged

            new_params = []                                                                                 # Build new parameter list for wrapper
            for param_name, param in sig.parameters.items():                                                # Process each original parameter
                if param_name == 'self':                                                                    # Skip self
                    continue
                if param_name in primitive_conversions:                                                     # Replace Type_Safe__Primitive with base type
                    _, primitive_type = primitive_conversions[param_name]                                   # Get the primitive type (str, int, float)
                    new_params.append(inspect.Parameter(                                                    # Create new parameter with primitive type
                        name=param_name,
                        kind=param.kind,
                        default=param.default,
                        annotation=primitive_type
                    ))
                elif param_name in type_safe_conversions:                                                   # Replace Type_Safe with BaseModel
                    _, basemodel_class = type_safe_conversions[param_name]                                  # Get the BaseModel class
                    new_params.append(inspect.Parameter(                                                    # Create new parameter with BaseModel type
                        name=param_name,
                        kind=param.kind,
                        default=param.default,
                        annotation=basemodel_class
                    ))
                else:
                    new_params.append(param)                                                                # Keep parameter unchanged

            wrapper.__signature__ = inspect.Signature(parameters=new_params)                                # Set new signature on wrapper

            wrapper.__annotations__ = {}                                                                    # Build new annotations dict
            for param_name, param_type in type_hints.items():                                               # Process each type hint
                if param_name in primitive_conversions:                                                     # Use primitive type for annotation
                    _, primitive_type = primitive_conversions[param_name]
                    wrapper.__annotations__[param_name] = primitive_type
                elif param_name in type_safe_conversions:                                                   # Use BaseModel for annotation
                    _, basemodel_class = type_safe_conversions[param_name]
                    wrapper.__annotations__[param_name] = basemodel_class
                elif param_name == 'return' and needs_return_conversion:                                    # Use BaseModel for return annotation
                    wrapper.__annotations__['return'] = basemodel_return
                else:
                    wrapper.__annotations__[param_name] = param_type                                        # Keep original annotation

            return self.add_route(function=wrapper, methods=['GET'])                                        # Add wrapped function as GET route
        else:
            return self.add_route(function=function, methods=['GET'])                                       # No conversion needed, add directly

    def add_route_post(self, function):
        return self.add_route_with_body(function, methods=['POST'])

    def add_route_put(self, function):
        return self.add_route_with_body(function, methods=['PUT'])

    def fast_api_utils(self):
        from osbot_fast_api.utils.Fast_API_Utils import Fast_API_Utils
        return Fast_API_Utils(self.app)

    def parse_function_name(self, function_name):                           # added support for routes that have resource ids in the path
        parts = function_name.split('__')
        path_segments = []

        for i, part in enumerate(parts):
            if i == 0:                                                  # First part is always literal
                path_segments.append(part.replace('_', '-'))
            else:
                if '_' in part:                                         # After __, check if it's a parameter or literal
                    subparts = part.split('_', 1)                       # Contains underscore, split into param and literal
                    path_segments.append('{' + subparts[0] + '}')
                    path_segments.append(subparts[1].replace('_', '-'))
                else:
                    path_segments.append('{' + part + '}')              # Just a parameter

        return '/' + '/'.join(path_segments)

    @index_by
    def routes(self):
        return self.fast_api_utils().fastapi_routes(router=self.router)

    def routes_methods(self):
        return list(self.routes(index_by='method_name'))

    def routes_paths(self):
        return list(self.routes(index_by='http_path'))

    def setup(self):
        self.setup_routes()
        self.app.include_router(self.router, prefix=self.prefix, tags=[self.tag])
        return self

    def setup_routes(self):     # overwrite this to add routes to self.router
        pass



    # def routes_list(self):
    #     items = []
    #     for route in self.routes():
    #         for http_methods in route.get('http_methods'):
    #             item = f'{http_methods:4} | {route.get("method_name"):14} | {route.get("http_path")}'
    #             items.append(item)
    #     return items