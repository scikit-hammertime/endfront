'use strict';

describe('Service: MedicinalProducts', function () {

  // load the service's module
  beforeEach(module('interactionsApp'));

  // instantiate service
  var MedicinalProducts;
  beforeEach(inject(function (_MedicinalProducts_) {
    MedicinalProducts = _MedicinalProducts_;
  }));

  it('should do something', function () {
    expect(!!MedicinalProducts).toBe(true);
  });

});
