'use strict';

describe('Service: Interactions', function () {

  // load the service's module
  beforeEach(module('interactionsApp'));

  // instantiate service
  var Interactions;
  beforeEach(inject(function (_Interactions_) {
    Interactions = _Interactions_;
  }));

  it('should do something', function () {
    expect(!!Interactions).toBe(true);
  });

});
