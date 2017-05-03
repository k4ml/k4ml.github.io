---
layout: post
title: Laravel tap function
tags:
  - laravel
  - php
  - method_missing
---

A friend shared Taylor Otwell [post about Laravel's tap function][1]. Basically what the function did was to do something with the passed object and then return it.

Reading the post, the `tap` function seem to root from Ruby on Rails community. It interesting I never see something like `tap` in Python sphere. Then Taylor go on sharing about the new `tap` implementation in Laravel 5.4. Looking at his example initially look weird and made me curious to know how it work.

I can't understand at first how this code basically possible:-

```
<?php
return tap($user)->update([
    'name' => $name,
    'age' => $age,
]);
```

Especially when he mentioned about the possibility of chaining even though `update()` is returning Boolean instead of the instance object. The magic basically lies in the usage of wrapper class that implement PHP's `__call` function.

```
<?php
    function tap($value, $callback = null)
    {
        if (is_null($callback)) {
            return new HigherOrderTapProxy($value);
        }
        $callback($value);
        return $value;
    }
```

The `HigherOrderTapProxy` class is implemented like [this][2] (comments removed for brevity):-

```
<?php
class HigherOrderTapProxy
{
    public $target;
    
    public function __construct($target)
    {
        $this->target = $target;
    }
    
    public function __call($method, $parameters)
    {
        $this->target->{$method}(...$parameters);
        return $this->target;
    }
}
```

As you can see, a method call on the instance of this class, will be proxied to the actual object through the `__call()` method. In PHP, if no method defined on the class, then it will try to call `__call()` method (if defined). This allow you to do some funky manipulation like forwarding the method call to some other instance like demonstrated above.

At this point it very clear it just some object proxy, using approach generally known as method_missing in Ruby. While in Python, you can implement the same thing using the `__getattr__` magic method.

[1]:https://medium.com/@taylorotwell/tap-tap-tap-1fc6fc1f93a6
[2]:https://github.com/laravel/framework/blob/5.4/src/Illuminate/Support/HigherOrderTapProxy.php
